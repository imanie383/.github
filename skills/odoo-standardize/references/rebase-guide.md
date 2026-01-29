# Interactive Rebase Guide for odoo-standardize

## Overview

When standardizing Odoo modules, issues may be detected in the `odoo-mig` log or pre-commit checks that require editing commits in the standardization branch. The most common scenario is editing the project template commit (`[REF] *: update CI files according to the project template`) to restore or modify configuration files.

This guide explains how to use the robust interactive rebase method that avoids manual vim/editor input.

## Problem with Standard Interactive Rebase

Standard `git rebase -i` requires manual editing:

```bash
git rebase -i HEAD~6
# This opens an editor where you must manually change "pick" to "edit"
# Then save and exit the editor
```

This is problematic when running in automated contexts because:
- Requires user to manually interact with an editor
- Can hang if editor is not configured correctly
- Difficult to automate in scripts

## Solution: GIT_SEQUENCE_EDITOR with sed

The robust approach uses `GIT_SEQUENCE_EDITOR` environment variable to inject a script that modifies the rebase todo file using sed:

```bash
#!/bin/bash
if [[ "$1" == *"git-rebase-todo"* ]]; then
    sed -i 's/^pick d65214d/edit d65214d/' "$1"
fi
```

This approach:
- ✅ Non-interactive
- ✅ Deterministic
- ✅ Fast
- ✅ Can be fully automated
- ✅ No user input required

## Using the Helper Scripts

### Option 1: Interactive Rebase Script

Use `interactive-rebase.sh` to mark a commit for editing:

```bash
./scripts/interactive-rebase.sh d65214d 6
```

Arguments:
- `d65214d` - The commit hash to edit
- `6` - Number of commits to include in rebase (default: 6)

This will:
1. Mark the commit `d65214d` for editing
2. Start the interactive rebase
3. Stop when it reaches the marked commit
4. Print instructions for the next steps

### Option 2: Manual Execution

If you prefer to create your own editor script:

```bash
# Create the editor script
cat > /tmp/rebase-editor.sh << 'EOF'
#!/bin/bash
if [[ "$1" == *"git-rebase-todo"* ]]; then
    sed -i 's/^pick d65214d/edit d65214d/' "$1"
fi
EOF
chmod +x /tmp/rebase-editor.sh

# Execute rebase with custom editor
GIT_SEQUENCE_EDITOR="/tmp/rebase-editor.sh" git rebase -i HEAD~6
```

## Workflow: Editing a Commit in the Branch

### Step 1: Identify the Commit

Find the commit that needs editing using `git log`:

```bash
git log --oneline
# Output:
# cd5864b [IMP] bibo: update External IDs to conform guidelines
# d1d0b0a [IMP] bibo: replace t-esc with t-out
# fa1b277 [IMP] bibo: use RST instead of markdown in the README
# c7b5f47 [IMP] bibo: modify license to OPL-1 and add LICENSE file
# bb332bc [IMP] bibo: reorganize data files by model naming convention
# d65214d [REF] *: update CI files according to the project template  <-- This one
# 18c8f3c [IMP] *: Apply pre-commit-vauxoo fixes
```

### Step 2: Count Commits

Count how many commits from HEAD to the commit you want to edit (including the commit itself):

```
HEAD (cd5864b)
  1. cd5864b
  2. d1d0b0a
  3. fa1b277
  4. c7b5f47
  5. bb332bc
  6. d65214d <-- Target commit (6 commits total)
```

### Step 3: Start Interactive Rebase

Use the helper script:

```bash
./scripts/interactive-rebase.sh d65214d 6
```

Or manually:

```bash
cat > /tmp/rebase-editor.sh << 'EOF'
#!/bin/bash
if [[ "$1" == *"git-rebase-todo"* ]]; then
    sed -i 's/^pick d65214d/edit d65214d/' "$1"
fi
EOF
chmod +x /tmp/rebase-editor.sh
GIT_SEQUENCE_EDITOR="/tmp/rebase-editor.sh" git rebase -i HEAD~6
```

Expected output:

```
Starting interactive rebase to edit commit d65214d...
Rebasing last 6 commits...

Rebasing (1/6)Stopped at d65214d...  [REF] *: update CI files according to the project template
You can amend the commit now, with

  git commit --amend

Once you are satisfied with your changes, run

  git rebase --continue
```

### Step 4: Make Changes

Edit the necessary files:

```bash
# For example, edit variables.sh to restore EXCLUDE_COVERAGE
nano variables.sh

# Or use other editors
vim variables.sh
code variables.sh
```

### Step 5: Stage and Amend

Stage your changes and amend the commit:

```bash
# Option A: Stage specific files
git add variables.sh

# Option B: Stage all changes
git add .

# Amend the commit with --no-edit to preserve the commit message
git commit --amend --no-edit
```

Or use the helper script:

```bash
./scripts/amend-and-continue-rebase.sh variables.sh
```

### Step 6: Continue Rebase

Continue the rebase to apply remaining commits:

```bash
git rebase --continue
```

The rebase will continue and apply all remaining commits. If there are conflicts, resolve them and continue.

### Step 7: Verify Changes

Verify that your changes are in the commit:

```bash
git show HEAD~5  # View the amended commit
```

Verify the full history:

```bash
git log --oneline
```

### Step 8: Force Push (if needed)

If the branch was already pushed to remote, use force push to update it:

```bash
git push --force-with-lease origin 15.0-standardize-module-user
```

**⚠️ Important:** Only force push to branches that you own and that haven't been merged. Never force push to main/master or shared branches.

## Common Scenarios

### Scenario 1: Restoring Missing Variables

**Problem:** `odoo-mig` removed important variables from `variables.sh`

**Action:**

1. Identify the commit that removed them (usually the project template commit)
2. Use interactive rebase to edit that commit
3. Restore the variables manually
4. Amend and continue

**Example:**

```bash
# Start rebase
./scripts/interactive-rebase.sh d65214d 6

# Edit variables.sh to add back:
# export EXCLUDE_COVERAGE="*/bibo/hooks.py,*/ks_dashboard_ninja/*"
# export EXCLUDE_LINT="ks_dashboard_ninja"

# Stage and amend
./scripts/amend-and-continue-rebase.sh variables.sh
```

### Scenario 2: Fixing README Configuration

**Problem:** `odoo-mig` didn't detect the correct runbot_id

**Action:**

1. Use interactive rebase to edit the project template commit
2. Update README.md with the correct runbot_id
3. Update both the badge URL and the repo link URL
4. Amend and continue

**Example:**

```bash
# Start rebase
./scripts/interactive-rebase.sh d65214d 6

# Edit README.md to fix runbot_id (change from default 0 to correct one)
nano README.md

# Stage and amend
./scripts/amend-and-continue-rebase.sh README.md
```

### Scenario 3: Correcting File Organization

**Problem:** XML files have incorrect structure or IDs

**Action:**

1. Use interactive rebase to edit the relevant commit
2. Fix the XML file structure
3. Amend and continue

## Troubleshooting

### "sed: can't read /tmp/rebase-editor.sh: No such file or directory"

The editor script path is incorrect or the file doesn't exist. Verify the path and permissions:

```bash
ls -l /tmp/rebase-editor.sh
cat /tmp/rebase-editor.sh
```

### "You are currently rebasing"

A rebase is in progress. You have three options:

```bash
# Continue the rebase
git rebase --continue

# Abort the rebase and return to the previous state
git rebase --abort

# Skip the current commit
git rebase --skip
```

### Changes not appearing in the commit

Verify you staged the files:

```bash
git status
```

If files are not staged, run:

```bash
git add <files>
git commit --amend --no-edit
git rebase --continue
```

### Rebase appears to hang

The editor may be waiting for user input. Press Ctrl+C and try a different approach:

```bash
git rebase --abort
# Try the helper script approach instead
./scripts/interactive-rebase.sh <commit-hash> <num-commits>
```

## Integration with odoo-standardize Workflow

When the odoo-standardize skill detects an issue that requires editing a commit:

1. ✅ Explain the issue to the user
2. ✅ Show what commit needs editing
3. ✅ Provide the exact changes to apply
4. ✅ Request user authorization
5. ✅ Use the interactive rebase method to edit the commit:
   ```bash
   ./scripts/interactive-rebase.sh <commit-hash> <num-commits>
   ```
6. ✅ Apply the changes
7. ✅ Stage and amend
8. ✅ Continue the rebase
9. ✅ Verify the changes
10. ✅ Force push if the branch was already pushed

## References

- [Git Rebase Documentation](https://git-scm.com/docs/git-rebase)
- [GIT_SEQUENCE_EDITOR Environment Variable](https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables#Plumbing-Environment-Variables)
- [Using sed for Search and Replace](https://www.gnu.org/software/sed/manual/sed.html)
