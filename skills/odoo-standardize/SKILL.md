---
name: odoo-standardize
description: This skill should be used when the user asks to "standardize a module", "run odoo-mig standardize", "estandarizar módulo", or needs to apply project conventions to an Odoo module. It guides through the complete standardization workflow including branch creation, odoo-mig execution, log analysis, pre-commit fixes, atomic commits, and robust interactive rebase using GIT_SEQUENCE_EDITOR for commit editing without manual editor interaction.
---

# Odoo Module Standardization

## Overview

Systematize the complete workflow for standardizing Odoo modules following project conventions. This includes creating branches, running standardization tools, analyzing logs, fixing issues with atomic commits, and preparing for PR submission.

## Prerequisites

Before starting, ensure the following are available:
- `odoo-mig` tool installed
- `pre-commit-vauxoo` tool installed
- `glab` CLI installed and configured (for MR creation)
- Git repository with a valid branch
- GitLab user (from `$GITLAB_USER` environment variable or prompt user)
- GitLab token (from `~/.gitlab_token` file or `$GITLAB_TOKEN` environment variable)

## Workflow

### Step 1: Gather Information

1. Request the module name from the user
2. Determine GitLab username:
   - Check `$GITLAB_USER` environment variable
   - If not set, ask the user for their GitLab username
3. Get current branch name with `git branch --show-current`

### Step 2: Create Branch

Create standardization branch following naming convention:

```bash
git checkout -b <current-branch>-standardize-<module>-<gitlab_user>
```

### Step 3: Execute Standardization

Determine if this is the first module or an additional module in the same project:

**First module** (or single module):
```bash
odoo-mig standardize <module> | tee /tmp/odoo-mig-standardize-<module>.log
```

**Additional modules** (when CI template was already applied):
```bash
odoo-mig standardize --skip-ci-template <module> | tee /tmp/odoo-mig-standardize-<module>.log
```

**Important:** The `--skip-ci-template` option must be placed BEFORE the module name argument.

**Detection logic:**
- Check if commits like `[IMP] *: Apply pre-commit-vauxoo fixes` or `[REF] *: update CI files according to the project template` already exist in the current branch
- If they exist, use `--skip-ci-template` to avoid duplicate project-level commits
- The `--skip-ci-template` option runs all module-level standardizations but skips project-level CI template and pre-commit fixes

### Step 4: Analyze odoo-mig Log

Review the log for incidences. Common issues to check:

| Incidence | Action Required |
|-----------|-----------------|
| `No runbot_id found in README.md` | Request correct runbot_id from user, apply via rebase to project template commit |
| `EXCLUDE_COVERAGE` removed from variables.sh | Restore the line via rebase to project template commit |
| `EXCLUDE_LINT` removed from variables.sh | Restore the line via rebase to project template commit |
| `OPENBLAS_NUM_THREADS` removed from variables.sh | Restore the line via rebase to project template commit |
| `PIP_USE_DEPRECATED` removed from variables.sh | Restore the line via rebase to project template commit |
| `ORCHESTSH="True"` added in VERSION < 15.0 | Remove the line via rebase to project template commit |

**For each incidence:**
1. Identify the correct commit where the fix should be applied
2. Explain why the correction is necessary
3. Provide exact code/changes to apply
4. **Wait for explicit user authorization before proceeding**
5. Apply rebase interactive using GIT_SEQUENCE_EDITOR method (see **Interactive Rebase Method** below)

### Interactive Rebase Method

To edit commits in the standardization branch robustly without manual editor interaction, use the GIT_SEQUENCE_EDITOR approach with sed:

**Using the helper script:**

```bash
# From the skill scripts directory:
./scripts/interactive-rebase.sh <commit-hash> <num-commits>

# Example: Edit commit d65214d (rebase last 6 commits)
./scripts/interactive-rebase.sh d65214d 6
```

**Manual approach (if helper script not available):**

```bash
cat > /tmp/rebase-editor.sh << 'EOF'
#!/bin/bash
if [[ "$1" == *"git-rebase-todo"* ]]; then
    sed -i 's/^pick <commit-hash>/edit <commit-hash>/' "$1"
fi
EOF
chmod +x /tmp/rebase-editor.sh
GIT_SEQUENCE_EDITOR="/tmp/rebase-editor.sh" git rebase -i HEAD~<num-commits>
```

**After rebase stops at the marked commit:**

1. Make changes to the required files
2. Stage changes: `git add <files>` or `./scripts/amend-and-continue-rebase.sh <files>`
3. Amend commit: `git commit --amend --no-edit`
4. Continue rebase: `git rebase --continue`

**Why this method?**
- ✅ Non-interactive (no vim/editor waiting for input)
- ✅ Deterministic and reproducible
- ✅ Can be fully automated
- ✅ Fast and reliable

For detailed guide with examples, see `references/rebase-guide.md`

### Step 5: Review Tests for setUp

Search for tests using `setUp` instead of `setUpClass`:

```bash
grep -r "def setUp(self)" <module>/tests/
```

If found, refactor to `setUpClass`:
1. Change `def setUp(self):` to `@classmethod` + `def setUpClass(cls):`
2. Change `super().setUp()` to `super().setUpClass()`
3. Replace `self.` with `cls.` for class attributes
4. Change helper methods called from setUpClass to `@classmethod`
5. Create atomic `[REF]` commit

### Step 6: Execute Pre-commit

Run pre-commit validation:

```bash
pre-commit-vauxoo -t all | tee /tmp/pre-commit-vauxoo-<module>.log
```

### Step 7: Analyze Pre-commit Errors

Separate errors by type:
- **MANDATORY**: Block the build, must be fixed
- **OPTIONAL**: Recommended fixes, do not block build

Common fixes:

| Error | Fix |
|-------|-----|
| `invalid-name` (variable too short) | Rename to descriptive name (e.g., `x` → `batch_index`) |
| `deprecated-pragma` (`disable-all`) | Change to `skip-file` |
| `consider-merging-classes-inherited` | Analyze if code should be moved to correct file (not always merge) |
| `setUp` in tests | Replace with `setUpClass` using `@classmethod` and `cls` |

**For each error:**
1. Propose atomic commit with exact changes
2. **Wait for explicit user authorization**
3. Apply fix and create commit

### Step 8: Verify

Repeat `pre-commit-vauxoo -t all` until all checks pass:
- Autofix checks: ✅ Passed
- Mandatory checks: ✅ Passed
- Optional checks: ✅ Passed

### Step 9: Push and Create Merge Request

1. Determine the correct remote for push:
   - Check available remotes with `git remote -v`
   - If `vauxoo-dev` remote exists, use it for push
   - Otherwise, use `origin`

2. **Wait for user confirmation before push**

3. Execute push if authorized:
   ```bash
   git push -u <remote> <branch-name>
   ```

4. Generate MR description based on actual commits:
   - Review commits with `git log --oneline <base-branch>..HEAD`
   - Create a bullet point for each meaningful change
   - Group related commits into single description items
   - Follow Odoo/OCA best practices for MR descriptions

5. Create Merge Request using glab:
   ```bash
   glab mr create --target-branch <base-branch> \
     --title "[IMP] <module>: clean and standardize code" \
     --description "$(cat <<'EOF'
   ## Summary

   Clean and standardize the `<module>` module to comply with project
   conventions and Odoo/OCA best practices.

   ## Changes

   ### Project-level
   - **CI/CD**: Update CI configuration files according to project template
   - **Code style**: Apply pre-commit-vauxoo automatic fixes

   ### <module>
   - **License**: Update license to OPL-1 and add LICENSE file
   - **Documentation**: Convert README to reStructuredText
   - <other changes based on actual commits>
   EOF
   )"
   ```

6. Return the MR URL to the user

**MR Description Guidelines:**
- Include only changes that were actually made
- Each bullet should describe what changed and why (when not obvious)
- Use format: `- **Category**: Description of change`
- Common categories: CI/CD, Code style, Data files, License, Documentation, Templates, Tests, Security, Performance
- **Keep description updated**: When adding new commits to an existing MR, update the description to reflect all changes using `glab mr update <mr-number> --description "..."`

## Golden Rules

- **Atomicity**: One commit = one type of correction
- **Order**: Clean step before advancing to next
- **Transparency**: Explain before modifying
- **Authorization**: Wait for explicit confirmation before applying changes
- **Remote History**: Never rewrite history if commits already exist on remote (unless user explicitly requests it)

## Commit Format

```
[{TAG}] {module_name}: {brief description}
```

**Tags:**
- `[FIX]` - Bug fixes
- `[REF]` - Refactoring
- `[ADD]` - New functionality
- `[REM]` - Remove code/files
- `[IMP]` - Improvements

**Rules:**
- Title: maximum 72 characters
- Body: wrap at 72 characters per line
- Use HEREDOC for commit messages:
  ```bash
  git commit -m "$(cat <<'EOF'
  [TAG] module: description

  Extended explanation if needed.
  EOF
  )"
  ```

## Learned Cases Reference

### Case: runbot_id Not Found

**Log indicator:** `ℹ️ No runbot_id found in README.md, will use default`

**Action:**
1. Ask user for correct runbot_id
2. Find the project template commit: `[REF] *: update CI files according to the project template`
3. Get commit hash and count commits to it: `git log --oneline | head -10`
4. Use interactive rebase:
   ```bash
   ./scripts/interactive-rebase.sh <commit-hash> <num-commits>
   ```
5. Update README.md with correct runbot_id in both badge URL and repo URL:
   - Badge: `https://runbot.vauxoo.com/runbot/badge/<RUNBOT_ID>/15.0.svg`
   - Link: `https://runbot.vauxoo.com/runbot/repo/git-git-vauxoo-com-vauxoo-<module>-git-<RUNBOT_ID>`
6. Stage and amend:
   ```bash
   ./scripts/amend-and-continue-rebase.sh README.md
   ```
   Or for multiple files:
   ```bash
   ./scripts/amend-and-continue-rebase.sh .
   ```
7. Rebase will continue automatically

### Case: EXCLUDE_COVERAGE, EXCLUDE_LINT, OPENBLAS_NUM_THREADS, or PIP_USE_DEPRECATED Removed

**Log indicator:** Variables missing from variables.sh diff

**Action:**
1. Identify which variables were removed (`EXCLUDE_COVERAGE`, `EXCLUDE_LINT`, `OPENBLAS_NUM_THREADS`, `PIP_USE_DEPRECATED`, etc.)
2. Find the project template commit (usually `[REF] *: update CI files according to the project template`)
3. Get commit hash and count commits to it: `git log --oneline | head -10`
4. Use interactive rebase:
   ```bash
   ./scripts/interactive-rebase.sh <commit-hash> <num-commits>
   ```
5. Restore the removed line(s) in variables.sh:
   ```bash
   export EXCLUDE_COVERAGE="*/bibo/hooks.py,*/ks_dashboard_ninja/*"
   export EXCLUDE_LINT="ks_dashboard_ninja"
   export OPENBLAS_NUM_THREADS="1"
   export PIP_USE_DEPRECATED="legacy-resolver"
   ```
   (Adjust values as needed for your project)
6. Stage and amend:
   ```bash
   ./scripts/amend-and-continue-rebase.sh variables.sh
   ```
7. Rebase will continue automatically

**Notes:**
- Always preserve `OPENBLAS_NUM_THREADS="1"` if it existed before the project template commit. This is required for numerical stability in Odoo environments.
- Always preserve `PIP_USE_DEPRECATED="legacy-resolver"` if it existed before. This ensures pip installs compatible versions of dependencies like `pycryptodome` (required by `pdfminer`). Without it, incompatible versions may be installed causing `NameError: name 'xrange' is not defined` errors.

### Case: ORCHESTSH Added in Version < 15.0

**Log indicator:** `export ORCHESTSH="True"` added to variables.sh in versions 14.0 or earlier

**CI Error:**
```
panic: config file not found: /root/.orchestsh/config.yml
```

**Cause:** The project template adds `ORCHESTSH="True"` which enables orchestsh in the Dockerfile, but projects with VERSION < 15.0 are not configured to use the orchestsh system.

**Action:**
1. Check the Odoo version in variables.sh: `grep VERSION variables.sh`
2. If VERSION is < 15.0, remove `export ORCHESTSH="True"` via interactive rebase
3. Find the project template commit: `[REF] *: update CI files according to the project template`
4. Get commit hash and count commits to it: `git log --oneline | head -10`
5. Use interactive rebase:
   ```bash
   ./scripts/interactive-rebase.sh <commit-hash> <num-commits>
   ```
6. Remove the `export ORCHESTSH="True"` line from variables.sh
7. Stage and amend:
   ```bash
   ./scripts/amend-and-continue-rebase.sh variables.sh
   ```
8. Rebase will continue automatically

**Prevention:** After applying the project template, always check if `ORCHESTSH` was added and verify the VERSION. If VERSION < 15.0 and ORCHESTSH was not in the original variables.sh, remove it immediately.

### Case: consider-merging-classes-inherited

**Pre-commit indicator:** `consider-merging-classes-inherited`

**Action:**
1. Analyze if code is in the wrong file
2. Check if model inheritance is split across files incorrectly
3. Move code to correct file (e.g., `ProductTemplate` from `product.py` to `product_template.py`)
4. Create atomic `[REF]` commit
5. **Do not blindly merge** - analyze the correct file structure first

### Case: invalid-name (short variable)

**Pre-commit indicator:** `Variable name "x" doesn't conform to pattern`

**Action:**
1. Find the variable in context
2. Propose descriptive name based on usage
3. Replace all occurrences
4. Create atomic `[FIX]` commit

### Case: deprecated-pragma

**Pre-commit indicator:** `Pragma "disable-all" is deprecated`

**Action:**
1. Replace `# pylint: disable-all` with `# pylint: skip-file`
2. Create atomic `[FIX]` commit

### Case: setUp in tests

**Indicator:** Tests using `def setUp(self):` instead of `setUpClass`

**Action:**
1. Change `def setUp(self):` to `@classmethod` + `def setUpClass(cls):`
2. Change `super().setUp()` to `super().setUpClass()`
3. Replace all `self.` with `cls.` for class attributes
4. Change helper methods called from setUpClass to `@classmethod` with `cls`
5. Create atomic `[REF]` commit

### Case: glab CLI Not Configured

**Indicator:** `glab auth status` returns authentication error

**Action:**
1. Check if glab is installed: `which glab`
2. If not installed, recommend: `sudo apt install glab`
3. Get GitLab hostname from remote URL: `git remote -v`
4. Configure glab with token:
   ```bash
   glab config set token "$(cat ~/.gitlab_token)" --host <gitlab-hostname>
   ```
5. Verify authentication: `glab auth status --hostname <gitlab-hostname>`

### Case: CI Warning - pdfminer Python library not found

**CI log indicator:** `WARNING ... odoo.addons.attachment_indexation.models.ir_attachment: Attachment indexation of PDF documents is unavailable because the 'pdfminer' Python library cannot be found`

**Cause:** The project depends on `enterprise` repo (via `oca_dependencies.txt`) which includes the `attachment_indexation` module. This module requires `pdfminer.six` but does not declare it in `external_dependencies`.

**Action:**
1. Check if `enterprise` is in `oca_dependencies.txt`
2. Add `pdfminer.six` to `requirements.txt`:
   ```
   # To avoid warnings in the module attachment_indexation
   pdfminer.six==20220319
   ```
3. Create atomic `[FIX]` commit:
   ```bash
   git add requirements.txt
   git commit -m "$(cat <<'EOF'
   [FIX] <main_module>: add pdfminer.six dependency for attachment_indexation

   This fixes the CI warning about the missing 'pdfminer' Python library
   required for PDF document indexation in the attachment_indexation module.
   EOF
   )"
   ```

**Detection:** This error cannot be detected before running CI because `attachment_indexation` does not declare `pdfminer` in its manifest `external_dependencies`. It only shows a runtime warning.

### Case: Data File Load Order in Manifest

**CI log indicator:** `External ID not found in the system: module.xml_id`

**Cause:** When `odoo-mig standardize` reorganizes data files, it may add them to the manifest in alphabetical order. However, if one file uses `ref()` to reference records defined in another file, the load order matters.

**Action:**
1. Identify which file defines the referenced `xml_id`
2. Ensure that file is listed **before** the file that references it in the manifest
3. Amend the change to the reorganization commit

**Example:**
```python
# Incorrect (ir_config_parameter uses ref to res_partner records)
"data/ir_config_parameter_data.xml",
"data/res_partner_data.xml",

# Correct
"data/res_partner_data.xml",
"data/ir_config_parameter_data.xml",
```

### Case: inheritable-method-lambda

**Pre-commit indicator:** `pylint: inheritable-method-lambda`

**Cause:** Using `default=_method_name` in field definitions instead of a lambda.

**Action:**
1. Change the default parameter to use lambda:
   ```python
   # Incorrect
   name = fields.Text(default=_default_credentials)

   # Correct
   name = fields.Text(default=lambda self: self._default_credentials())
   ```
2. Create atomic `[FIX]` commit

## Multiple Modules Workflow

When standardizing multiple modules in the same project/repository, use the same branch and MR:

```bash
# First module: creates branch and applies all standardizations
odoo-mig standardize module_a

# Additional modules: skip CI template (already applied)
odoo-mig standardize module_b --skip-ci-template
odoo-mig standardize module_c --skip-ci-template

# Push all changes together
git push -u <remote> <branch-name>

# Create single MR for all modules
glab mr create --title "[IMP] module_a, module_b, module_c: clean and standardize code"
```

### MR Title Format for Multiple Modules

```
[IMP] module_a, module_b, module_c: clean and standardize code
```

### MR Description Format for Multiple Modules

```markdown
## Summary

Clean and standardize the `module_a`, `module_b`, and `module_c` modules to comply with
project conventions and Odoo/OCA best practices.

## Changes

### Project-level
- **CI/CD**: Update CI configuration files according to project template
- **Code style**: Apply pre-commit-vauxoo automatic fixes
- **Dependencies**: <if any Python dependencies were added>

### module_a
- **License**: Update license to OPL-1 and add LICENSE file
- **Documentation**: Convert README to reStructuredText
- ...

### module_b
- **License**: Update license to OPL-1 and add LICENSE file
- **Documentation**: Convert README to reStructuredText
- ...

### module_c
- **License**: Update license to OPL-1 and add LICENSE file
- ...
```
