<!-- AGENT MANDATE: ALWAYS update this changelog whenever changes are made. Keep newest entries at the very top. Always include semantic version and build numbers. -->

# Changelog

All notable changes to the **Bach in the Mirror** (Mozart Transposition Engine) project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-10-09

### Added
- **GitHub Pages Packaging Script (`package-pages.sh`)**:
  - Created standalone packaging script that packages the `frontend/` directory (viewer HTML, manuscript autograph scans, `.nojekyll`, and all 1,522 rendered score PNGs) into a deployment-ready `gh-pages` branch.
  - Uses isolated git plumbing (`git write-tree`, `git commit-tree`, `git update-ref`) to package assets without switching git branches or touching the user's active working tree.
  - Added `-p` / `--push` flag to automatically push to `origin gh-pages`.
  - Added `make pages` and `make deploy` targets in `Makefile`.
  - Added `package.json` with `npm run package` and `npm run deploy` scripts.

### Fixed & Enhanced
- **Single-Page PNG Output Normalization (`mozart-make.py`)**:
  - Resolved build issue where single-page scores were never skipped on repeated `make` runs (LilyPond outputs `<file>.png` for 1-page scores rather than `<file>-page1.png`).
  - Added automatic aliasing of `<file>.png` to `<file>-page1.png` when single-page outputs are produced or detected in cache.
  - Ensured all 720 score targets across all 15 inventions are reliably skipped (0.05s build time) when up to date.
  - Fixed broken image (404) rendering in `frontend/index.html` for single-page scores (such as Invention 04 in mode 2, and Invention 10 in mode 1).
- **Web Frontend Modernization & Redesign (`frontend/index.html`)**:
  - Completely redesigned the frontend with modern HTML5 semantics, responsive CSS custom properties, and elegant classical typography.
  - Implemented accessible native `<dialog>` modals for "About & Bilateral Theory", "Practice & Performance Guide", and "Keyboard Shortcuts".
  - Replaced inline JavaScript attributes with structured DOM event listeners.
  - Added live context banner displaying resolved transposed key (e.g. `E♭ Major (+3 st)`), original key, BWV numbers, mirroring mode, and symmetry axis (Split 56).
  - Added hands-free piano keyboard shortcuts (`←`/`→` for inventions, `↑`/`↓` for semitone transpositions, `M` for mode cycling, `A` for autograph toggle, `L` for book spread vs stacked layout, `?` for help).
  - Added URL parameter persistence and share button with toast notification.
  - Replaced Windows-style backslashes (`autograph\\...`) with web-standard forward slashes (`autograph/...`) for autograph scans.
  - Fixed page 3 score image URL pathing from `'' + filename + '\\...'` to `dirnpath + ...` for 3-page inventions (Inventions 05, 12, 14).
  - Fixed page 3 score card visibility bug where `.score-card { display: flex; }` overrode the HTML `hidden` attribute, causing a ghost 3rd card to display on 2-page scores (such as Invention 01). Added strict `[hidden], .score-card.is-hidden { display: none !important; }` enforcement.
  - Added self-healing image loader with loading indicators that automatically hides extra page cards if a score fits on fewer pages.
- **Stale Output Cleanup Before Rendering (`mozart-make.py`)**:
  - Removed outdated page PNG files matching `{lilypond_output_file}*.png` prior to re-engraving to prevent stale multi-page artifacts when a score fits on fewer pages.
- **Version Bump**:
  - Bumped `mozart-make.py` to version 2.2.

---

## [2.1.0] - 2026-09-20

### Added
- **Score Beautifier Engine (`score_beautifier.py`)**:
  - Created standalone post-processor module to clean intermediate `.ly` files before LilyPond engraving.
  - Strips erratic, measure-by-measure `\ottava` statements, cleans stacked duplicates, and enforces clean whitespace formatting.
  - Integrated into `mozart-make.py` worker pipeline between transpilation and image compilation.

### Fixed & Enhanced
- **Octave Normalization for Playable Symmetrical Inversion (`mozart-compile.py`)**:
  - Resolved root causes of extreme ledger lines (up to 8 lines below the treble staff and 5 lines below the bass staff).
  - Applied $+1$ octave transposition (`\transpose c c'`) to inverted voices, shifting inverted Voice 1 into standard Right Hand range ($A3$–$E6$) and inverted Voice 2 into standard Left Hand range ($E2$–$E4$).
  - 100% preserved bilateral mirror fingering symmetry (interval geometries and finger motions remain exact mirror opposites).
- **Eliminated Ottava Churn (`mozart-compile.py`)**:
  - Removed flawed `find_octava()` line-by-line injections from `process_one_block()` and `transpose()`, terminating broken, flickering `8 - - - 1` brackets.
- **Contextual Clef Preservation (`mozart-compile.py`)**:
  - Preserved Bach's authentic clef shifts (e.g. `\clef "treble"` in mm. 9–12 and `\clef "bass"` in m. 13 of Invention 1) for un-inverted voices, eliminating high ledger lines in Voice 2.
- **Version Bumps**:
  - Updated `mozart-compile.py` and `mozart-make.py` to version 2.1.

### Verified
- **Invention 01 Full Mode & Key Matrix**: Rebuilt all 48 scores (Modes 0, 1, 2, 3 across all 12 keys) in 11.4s with 0 errors. Verified publication-quality engraving with minimal, natural ledger lines and zero erratic ottava brackets.

---

## [2.0.0] - 2026-09-20

### Added
- **Multi-Worker Parallelism (`mozart-make.py`)**:
  - Implemented concurrent task execution using a worker thread pool, enabling massive build speedups across all 12 transpositions and 15 inventions.
  - Added `-j` / `--jobs` CLI argument for custom concurrency control.
  - Added `-m` / `--modes` CLI argument to select mirroring modes, with all 4 modes (0=No Mirroring, 1=Left Hand Ascending, 2=Right Hand Descending, 3=Mirror Image) enabled by default.
  - Added `-f` / `--force` CLI argument to bypass timestamp caching and force regeneration.
  - Added dynamic processor detection via `os.cpu_count()` (no hardcoded core counts).
  - Added synchronized, clean progress indicators `[X/180] (XX%)` with execution summary statistics.
  - Added flexible target selection: builds all 15 inventions by default, with support for `--all` or specific invention numbers (e.g. `01 02`).
- **Documentation & Benchmarks (`readme.md`)**:
  - Overhauled `readme.md` with complete documentation covering bilateral keyboard symmetry, mirroring modes, build methods, architecture diagrams, and multi-core scaling benchmarks.
- **Makefile Integration (`Makefile`)**:
  - Added root `Makefile` supporting standard build commands (`make`, `make -j8`, `make clean`, and individual targets like `make 01`).
  - Implemented dynamic core detection in Makefile querying `getconf _NPROCESSORS_ONLN`, `nproc`, and `sysctl -n hw.ncpu`.

### Fixed
- **Invention 09 Markup Ottava Splitting**:
  - Fixed multiline `\markup` in `mozart-transpose-input/09.ly` that caused `mozart-compile.py` to inject `\ottava` inside markup blocks, resolving LilyPond compilation failures for Invention 09.

### Verified
- **Full Library Generation**: Successfully compiled all 15 Bach Two-Part Inventions (180 scores, 384 PNG pages) in parallel in under 45 seconds.

---

## [1.2.1] - 2026-09-20

### Changed
- **Driver & Build Automation (`build.sh`)**:
  - Rewrote `build.sh` with `bash` strict mode (`set -euo pipefail`).
  - Added automatic nuking and recreation of `mozart-transpose-output/tmp/` prior to build runs to prevent stale file conflicts.
  - Added dynamic resolution of the Python virtual environment interpreter (`.venv/bin/python`).
  - Added auto-creation of output directories and synchronization of rendered PNGs to `frontend/png/`.
- **Driver Script Fixes (`mozart-make.py`)**:
  - Switched `input_file_path` from obsolete `working/` directory to `mozart-transpose-input/`.
  - Replaced hardcoded `python3` invocations with `sys.executable` to guarantee execution inside the virtual environment.
  - Updated shebang to `#!/usr/bin/env python3`.

---

## [1.2.0] - 2026-09-20

### Added
- **Isolated Python Virtual Environment (`.venv/`)**: Set up dedicated local Python virtual environment with `python-ly` (version 0.9.10) installed.
- **Dynamic Binary Resolution**: Updated `mozart-compile.py` to auto-resolve the `ly` binary via `shutil.which()`, `sys.prefix`, and fallback to Python module execution (`sys.executable -m ly`), eliminating rigid system path assumptions.
- **Auto Directory Creation**: Enhanced `mozart-compile.py` to automatically create parent directories for output target files (`os.makedirs`) if they do not yet exist.
- **Agents Knowledge Base (`agents.md`)**: Created comprehensive agent documentation covering symmetrical inversion philosophy, project architecture, standing development rules, and the future MusicXML transformation roadmap.
- **Expanded `.gitignore`**: Added `.venv/`, `__pycache__/`, `*.pyc`, `.vscode/`, and `.DS_Store` to maintain a clean git repository.

### Fixed
- **Virtual Environment Subprocess Execution**: Fixed `mozart-compile.py` subprocess invocation of `ly` to use `sys.executable` instead of system `python3`, ensuring virtual environment packages are correctly loaded without `ModuleNotFoundError`.
- **Python 3.12+ String Escape Warnings**: Replaced unescaped backslashes in LilyPond block templates and command strings (`\ottava`, `\header`, `\clef`, `\markup`, `\score`, `\context`, `\layout`) with properly escaped backslashes.

### Verified
- **End-to-End Transpilation**: Successfully verified `mozart-compile.py` execution against `mozart-transpose-input/01.ly`, generating `mozart-transpose-output/tmp/0_01_3_6.ly` and compiling via LilyPond 2.26.0 without errors.

---

## [1.1.0] - 2021-09-26

### Changed
- Cleanup and updates to support Linux environments.
- Improved octava range handling and detection.

---

## [1.0.0] - 2020-06-27

### Added
- Initial release of Mozart Transposition Engine and Bach in the Mirror score generator by Benjamin Pritchard / Kundalini Software.
- Initial handcrafted tokenizer and LilyPond file generation for Bach Two-Part Inventions.
- Batch driver `mozart-make.py` for rendering multiple transpositions and mirror modes.

