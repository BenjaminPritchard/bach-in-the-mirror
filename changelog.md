<!-- AGENT MANDATE: ALWAYS update this changelog whenever changes are made. Keep newest entries at the very top. Always include semantic version and build numbers. -->

# Changelog

All notable changes to the **Bach in the Mirror** (Mozart Transposition Engine) project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

