<!-- AGENT MANDATE: ALWAYS update this changelog whenever changes are made. Keep newest entries at the very top. Always include semantic version and build numbers. -->

# Changelog

All notable changes to the **Bach in the Mirror** (Mozart Transposition Engine) project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

