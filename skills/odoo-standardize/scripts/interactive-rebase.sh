#!/bin/bash
#
# Interactive Rebase Helper for Git Rebase --edit
#
# This script provides a robust, non-interactive way to perform git rebase -i,
# marking a specific commit for editing using GIT_SEQUENCE_EDITOR and sed.
# Avoids the need for manual vim/editor input during interactive rebase.
#
# Usage:
#   ./interactive-rebase.sh <commit-hash> [num-commits]
#
# Arguments:
#   commit-hash    - The commit hash to mark for editing
#   num-commits    - Number of commits to include in rebase (default: 6)
#
# Examples:
#   # Mark commit d65214d for editing (rebase last 6 commits)
#   ./interactive-rebase.sh d65214d 6
#
#   # Mark commit 3e49133 for editing (rebase last 5 commits)
#   ./interactive-rebase.sh 3e49133 5
#
# After rebase starts:
#   1. Make changes to files
#   2. Stage changes with: git add <files>
#   3. Amend the commit with: git commit --amend --no-edit
#   4. Continue the rebase with: git rebase --continue

set -e

COMMIT_HASH="$1"
NUM_COMMITS="${2:-6}"

if [[ -z "$COMMIT_HASH" ]]; then
    echo "Usage: $0 <commit-hash> [num-commits]"
    echo ""
    echo "Example:"
    echo "  $0 d65214d 6"
    exit 1
fi

# Create a temporary editor script that marks the specified commit for editing
EDITOR_SCRIPT=$(mktemp)
trap "rm -f $EDITOR_SCRIPT" EXIT

# Create the editor that will modify the rebase todo file
# It uses sed to change "pick <commit-hash>" to "edit <commit-hash>"
cat > "$EDITOR_SCRIPT" << EDITOR_EOF
#!/bin/bash
if [[ "\$1" == *"git-rebase-todo"* ]]; then
    sed -i 's/^pick $COMMIT_HASH/edit $COMMIT_HASH/' "\$1"
fi
EDITOR_EOF

chmod +x "$EDITOR_SCRIPT"

# Execute interactive rebase with the custom editor
echo "Starting interactive rebase to edit commit $COMMIT_HASH..."
echo "Rebasing last $NUM_COMMITS commits..."
echo ""
GIT_SEQUENCE_EDITOR="$EDITOR_SCRIPT" git rebase -i HEAD~$NUM_COMMITS

echo ""
echo "✓ Rebase stopped at commit $COMMIT_HASH for editing"
echo ""
echo "Next steps:"
echo "  1. Make your changes to files"
echo "  2. Stage changes:     git add <files>"
echo "  3. Amend the commit:  git commit --amend --no-edit"
echo "  4. Continue rebase:   git rebase --continue"
