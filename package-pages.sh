#!/usr/bin/env bash
set -euo pipefail

# package-pages.sh
# Packages the frontend/ application (HTML viewer, autograph scans, and rendered score PNGs)
# into a clean 'gh-pages' branch for deployment on GitHub Pages (github.io).
#
# Usage:
#   ./package-pages.sh            # Packages frontend into local 'gh-pages' branch
#   ./package-pages.sh --push     # Packages and pushes 'gh-pages' to origin
#   ./package-pages.sh --orphan   # Packages as a standalone orphan commit (no parent history)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BRANCH="gh-pages"
DO_PUSH=false
ORPHAN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--push)
            DO_PUSH=true
            shift
            ;;
        -o|--orphan)
            ORPHAN=true
            shift
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -p, --push       Push packaged branch to origin"
            echo "  -o, --orphan     Create fresh orphan commit without parent history"
            echo "  -b, --branch     Target branch name (default: gh-pages)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Run '$0 --help' for usage." >&2
            exit 1
            ;;
    esac
done

# Verify frontend directory and rendered score assets
if [ ! -d "frontend" ] || [ ! -f "frontend/index.html" ]; then
    echo "Error: frontend/index.html not found." >&2
    exit 1
fi

PNG_COUNT=$(find frontend/png -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PNG_COUNT" -eq 0 ]; then
    echo "Warning: frontend/png/ contains 0 PNG files." >&2
    echo "Run 'make' first to generate all scores before packaging." >&2
    exit 1
fi

echo "Found $PNG_COUNT rendered score images in frontend/png/."
echo "Packaging frontend into branch '$BRANCH'..."

# Create clean temporary staging worktree and independent git index
TMP_DIR=$(mktemp -d)
INDEX_FILE="$(mktemp -u)"

cleanup() {
    rm -rf "$TMP_DIR"
    rm -f "$INDEX_FILE"
}
trap cleanup EXIT

# Stage frontend assets
cp -R frontend/* "$TMP_DIR"/
touch "$TMP_DIR/.nojekyll"

GIT_DIR="$(git rev-parse --git-dir)"
export GIT_DIR
export GIT_WORK_TREE="$TMP_DIR"
export GIT_INDEX_FILE="$INDEX_FILE"

git add -A -f
TREE_ID=$(git write-tree)

# Determine parent commit unless orphan mode is requested
PARENT_ARGS=()
if [ "$ORPHAN" = false ] && git rev-parse --verify "refs/heads/$BRANCH" >/dev/null 2>&1; then
    PARENT_ARGS=("-p" "$(git rev-parse "refs/heads/$BRANCH")")
fi

TIMESTAMP=$(date -u +'%Y-%m-%d %H:%M:%S UTC')
COMMIT_ID=$(git commit-tree "$TREE_ID" "${PARENT_ARGS[@]}" -m "Deploy Bach in the Mirror frontend ($TIMESTAMP)")

git update-ref "refs/heads/$BRANCH" "$COMMIT_ID"

echo "------------------------------------------------------------"
echo "Successfully packaged frontend into '$BRANCH' ($COMMIT_ID)."
echo "  Files staged: $(find "$TMP_DIR" -type f | wc -l | tr -d ' ')"
echo "------------------------------------------------------------"

if [ "$DO_PUSH" = true ]; then
    echo "Pushing '$BRANCH' to origin..."
    git push origin "$BRANCH"
    echo "Deployment complete! Live at: https://benjaminpritchard.github.io/bach-in-the-mirror/"
else
    echo "To push to GitHub and publish to GitHub Pages, run:"
    echo "    git push origin $BRANCH"
    echo ""
    echo "One-time GitHub setup:"
    echo "  1. Visit: https://github.com/BenjaminPritchard/bach-in-the-mirror/settings/pages"
    echo "  2. Under 'Source', select 'Deploy from a branch'"
    echo "  3. Select branch '$BRANCH' and folder '/ (root)'"
    echo "  4. Live site: https://benjaminpritchard.github.io/bach-in-the-mirror/"
fi
