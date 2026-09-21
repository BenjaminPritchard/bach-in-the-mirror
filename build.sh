#!/usr/bin/env bash
set -euo pipefail

# bach-in-the-mirror build driver
# Resolves script directory, cleans temporary workspace, and runs under the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nuke and recreate temporary directory for mozart-compile intermediate files
echo "Cleaning temporary transposition workspace: mozart-transpose-output/tmp/"
rm -rf mozart-transpose-output/tmp
mkdir -p mozart-transpose-output/tmp

# Ensure output directories exist
mkdir -p mozart-transpose-output/png
mkdir -p frontend/png

# Resolve virtual environment Python interpreter
if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/.venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_EXEC="$VIRTUAL_ENV/bin/python"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_EXEC="$(command -v python3)"
else
    echo "Error: Python interpreter not found." >&2
    exit 1
fi

echo "Using Python interpreter: $PYTHON_EXEC"

# Execute driver with forwarded arguments (e.g. -j14, 01, --all)
"$PYTHON_EXEC" mozart-make.py "$@"

# Copy generated PNG score files to frontend
if compgen -G "mozart-transpose-output/png/*.png" > /dev/null; then
    echo "Syncing rendered PNG scores to frontend/png/"
    cp -f mozart-transpose-output/png/*.png frontend/png/
fi

echo "Build complete."