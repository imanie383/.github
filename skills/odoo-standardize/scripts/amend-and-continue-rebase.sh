#!/bin/bash
#
# Amend Commit and Continue Rebase
#
# Convenience script that automates the common workflow of:
#   1. Staging changes: git add <files>
#   2. Amending the current commit: git commit --amend --no-edit
#   3. Continuing the rebase: git rebase --continue
#
# Usage:
#   ./amend-and-continue-rebase.sh [files...]
#
# Examples:
#   # Stage specific files and amend
#   ./amend-and-continue-rebase.sh variables.sh README.md
#
#   # Stage all changes and amend
#   ./amend-and-continue-rebase.sh .

set -e

if [[ -z "$1" ]]; then
    echo "Usage: $0 [files...]"
    echo ""
    echo "Examples:"
    echo "  # Stage specific files"
    echo "  $0 variables.sh README.md"
    echo ""
    echo "  # Stage all changes"
    echo "  $0 ."
    exit 1
fi

echo "Staging changes..."
git add "$@"

echo "Amending commit..."
git commit --amend --no-edit

echo ""
echo "Continuing rebase..."
git rebase --continue

echo ""
echo "✓ Rebase continued successfully"
