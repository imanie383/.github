---
name: odoo-migrate
description: Expert autonomous Odoo migration assistant for all versions (8.0-19.0). Use when working with Odoo version migrations (any source→target), executing migrations with odoo-mig, fixing migration errors, running tests, and creating merge requests. Handles Community, Enterprise, OCA, and custom modules. Autonomously executes migrations, investigates errors, applies fixes with pre-commit validation, and creates MRs via glab.
---

# Odoo Migration Expert

Senior-level autonomous agent for Odoo version migrations (8.0-19.0). Executes migrations, fixes issues, validates code, and creates merge requests without user intervention.

## Prerequisites

Before starting, verify the following:
- `odoo-mig` tool installed
- `pre-commit-vauxoo` tool installed
- `glab` CLI installed and configured
- Git repository with a valid branch
- GitLab credentials: `$GITLAB_USER` env var or prompt, token from `~/.gitlab_token` or `$GITLAB_TOKEN`

## Core Workflow

1. **Validate prerequisites** → Check tools and credentials are available
2. **Execute migration** → Run `odoo-mig migrate` on target module
3. **Analyze output** → Parse migration log, categorize errors
4. **Fix iteratively** → Apply fix + run `pre-commit-vauxoo` after each change
5. **Test** → Run Odoo tests, repeat fixes if needed
6. **Document with references** → Use `odoo-commit-finder` to find Odoo commits that justify changes
7. **Create MR** → Use `glab mr create` with commit references included

## Mandatory Rules for View/XPath Changes

**These rules are non-negotiable and must be followed without exception.**

### Rule: Never Remove or Simplify XPaths

When an xpath or view inheritance error occurs, removing or simplifying the xpath is **FORBIDDEN**.

The only valid approaches are:
1. **Refactor** - Adapt the xpath to the new structure while preserving functionality
2. **Document native replacement** - If Odoo now includes the functionality natively, document why removal is valid
3. **Ask user** - If functionality would be lost with no equivalent, get explicit approval

### XPath Investigation Checklist

Before modifying ANY xpath that produces an error, complete this checklist:

- [ ] **Identified original purpose**: What does this xpath add/modify/hide?
- [ ] **Searched target Odoo source**: Used grep/cat to find equivalent element
- [ ] **Documented the mapping**: OLD xpath → NEW xpath (with file:line reference)
- [ ] **Verified functionality preserved**: The refactored xpath provides same behavior

If you cannot complete this checklist, STOP and ask the user for guidance.

### Anti-patterns (What NOT to do)

**WRONG - Removing xpath:**
```xml
<!-- Removed because element doesn't exist in v19 -->
```

**WRONG - Simplifying template:**
```xml
<!-- Simplified version - removed custom price columns -->
<template id="report" inherit_id="sale.report">
    <!-- Only basic functionality kept -->
</template>
```

**CORRECT - Proper investigation and refactor:**
```xml
<!-- Migration v16→v19:
     OLD: //td[@name='td_taxes'] (removed in v19)
     NEW: //td[@name='td_product_taxes'] (found in sale/report/ir_actions_report_templates.xml:235)
-->
<td name="td_product_taxes" position="attributes">
    <attribute name="invisible">1</attribute>
</td>
```

## Version Detection

If the source version is not specified, detect it from the module's `__manifest__.py`:

```bash
# Extract version from manifest (format: "X.0.1.0.0" where X.0 is Odoo version)
grep -oP '["'\'']version["\'\']\s*:\s*["\'\']\K[0-9]+\.[0-9]+' /path/to/module/__manifest__.py
```

The version field follows the format `{odoo_version}.{module_version}`:
- `"version": "17.0.1.0.0"` → Odoo 17.0
- `"version": "16.0.2.1.0"` → Odoo 16.0
- `"version": "18.0.1.0.0"` → Odoo 18.0

**Always detect source version if user only specifies target version.**

## Migration Execution

Execute migration using odoo-mig:

```bash
# Execute migration and capture log
odoo-mig migrate /path/to/module --from X.0 --to Y.0 2>&1 | tee migration.log

# Example: Migrate module from 17.0 to 18.0
odoo-mig migrate ./my_module --from 17.0 --to 18.0 2>&1 | tee migration.log

# If source version not specified, detect it first:
SOURCE_VERSION=$(grep -oP '["'"'"']version["'"'"']\s*:\s*["'"'"']\K[0-9]+\.[0-9]+' ./my_module/__manifest__.py)
odoo-mig migrate ./my_module --from $SOURCE_VERSION --to 18.0 2>&1 | tee migration.log
```

After execution:
1. Read `migration.log` for errors and warnings
2. Identify version range to check in `references/version_critical_changes.md`
3. Categorize errors: Import, Field, View, API, Database

## Fix and Validate Cycle

For each error found:

1. **Identify error type** → Check `references/fix_patterns.md` for manual patterns
2. **Apply fix** → Use pattern from fix_patterns.md or common_issues.md
3. **Run pre-commit** → `pre-commit-vauxoo`
4. **Stage changes** → `git add -u` (if pre-commit modified files)
5. **Repeat** for next error

**Fix order priority:**
1. Import/syntax errors (block everything)
2. Model/field changes
3. View updates
4. API/logic fixes

**References:**
- `references/fix_patterns.md` → Manual patterns by version (attrs, hooks, tree→list, Domain API)
- `references/common_issues.md` → General troubleshooting

### XPath/View Inheritance Errors - Special Handling

When the error involves xpath or view inheritance:

1. **STOP** - Do not proceed to fix without investigation
2. **Read the failing xpath** in your module's XML file
3. **Find the base view** in target Odoo: `~/instance/odoo/addons/{module}/views/`
4. **Search for the element**: `grep -rn "name='{element}'" ~/instance/odoo/addons/{module}/`
5. **Complete the Investigation Checklist** (see Mandatory Rules section)
6. **Apply refactored xpath** preserving original functionality
7. **Run pre-commit** and continue

Never skip steps 1-5. If you find yourself wanting to "simplify" or "remove for now", that is a signal you have not completed the investigation.

#### Common Element Renames (v19.0)

| Old Pattern | New Pattern |
|-------------|-------------|
| `td name="td_taxes"` | `td name="td_product_taxes"` |
| `th name="th_taxes"` | `th name="th_product_taxes"` |
| `th name="th_discount"` | `th name="th_product_discount"` |
| `td name="td_discount"` | `td name="td_product_discount"` |
| `div[@data-key='app']` | `block[@id='container']` |
| `doc.order_line` | `lines_to_report` |

For full reference, see `references/version_critical_changes.md`.

## Investigation Priority

For each error, investigate in order:

1. **Local references (fastest):**
   - `references/version_critical_changes.md` → Breaking changes per version
   - `references/fix_patterns.md` → Manual fix patterns
2. **OCA Migration Wiki** → `https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-{VERSION}` (focused on migration)
3. **Context7 (optional)** → Up-to-date Odoo documentation when above sources insufficient
4. **Context7: OpenUpgrade** → Migration scripts and upgrade analysis
5. **Odoo Community source** → `~/instance/odoo/addons/module_name/`
6. **Enterprise/OCA** → `~/instance/enterprise/` and `~/instance/extra_addons/`

For detailed strategies, see `references/debugging_strategies.md`.

## Testing

Execute tests after all fixes applied:

```bash
dropdb odoo_test 2>/dev/null || /entrypoint.sh
createdb odoo_test
odoo-bin --database=odoo_test --test-enable -i module_name --stop-after-init --log-level=test 2>&1 | tail -100
```

If tests fail, return to Fix and Validate Cycle.

## Commit Documentation with References

After all fixes are applied and tests pass, document the changes with official Odoo commit references using the `odoo-commit-finder` skill.

### Why Document with References?

Migration commits should reference the official Odoo commits that introduced breaking changes. This:
- Provides traceability for code reviewers
- Documents the rationale behind each change
- Links to PR discussions with full context
- Follows professional migration standards

### Workflow: Analyze Changes and Find References

1. **Analyze applied changes** - Review git diff to identify migration-related modifications:
   ```bash
   git diff --staged --name-only  # List modified files
   git diff --staged              # See actual changes
   ```

2. **Categorize changes** - Group changes by type:
   - Field renames (e.g., `deprecated` → `active`)
   - Method changes (e.g., `map_accounts` → `map_account`)
   - View syntax changes (e.g., `<tree>` → `<list>`)
   - Attribute removals (e.g., `string` attribute in search views)
   - API deprecations
   - POS architecture changes (registries → OWL)
   - Translation patterns (`_()` → `self.env._()`)

3. **Find reference commits** - Use `odoo-commit-finder` skill to find official Odoo commits:
   - Search for EVERY change that modifies code behavior
   - Don't skip changes just because they seem "obvious"

   **Example: Field rename**
   > "dame el commit del cambio de deprecated a active en account.account"

   **Example: Method refactor**
   > "busca el commit de map_accounts renamed to map_account"

   **Example: View element change**
   > "encuentra el commit de tree changed to list in views"

5. **Collect commit references** - Format found commits with numbered references and GitHub URLs:
   ```
   Changes:
   - Renamed field `deprecated` to `active` in account.account [1]
   - Replaced `map_accounts(dict)` with `map_account(account)` [2]
   - Applied prefer-env-translation pattern (self.env._ instead of _) [3]
   - Updated POS assets bundle to point_of_sale._assets_pos [4]

   Refs:
   [1]: https://github.com/odoo/odoo/commit/d44f9247
   [2]: https://github.com/odoo/odoo/commit/be0a56ea
   [3]: https://github.com/odoo/odoo/commit/b794f0f3
   [4]: https://github.com/odoo/odoo/commit/c313f591
   ```

   **IMPORTANT**: Always use **8-character hashes** for commit references.

### Reference Prioritization

Not all changes need references. Prioritize:

| Priority | Change Type | Reference Required |
|----------|-------------|-------------------|
| High | Field renames | Yes - affects data migration |
| High | Method removals/renames | Yes - affects custom code |
| Medium | View element changes | Yes - documents structural changes |
| Medium | API deprecations | Yes - future compatibility |
| Low | Syntax updates (attrs→invisible) | Optional - well-documented in wiki |
| Low | Import path changes | Optional - usually obvious |

### Automated Change Detection

Before creating the commit, analyze the diff to extract change patterns:

```bash
# Find field changes in Python files
git diff --staged -- "*.py" | grep -E "^\+.*=.*fields\." | head -10

# Find view element changes in XML files
git diff --staged -- "*.xml" | grep -E "^\+.*<(list|tree|form)" | head -10

# Find removed/changed method calls
git diff --staged -- "*.py" | grep -E "^-.*def |^\+.*def " | head -10
```

For each detected change type, invoke the corresponding search in `odoo-commit-finder`.

## Merge Request Creation

After all tests pass and commit references are collected, create MR automatically:

```bash
# Ensure all changes committed with references
git add -A
git commit -m "$(cat <<'EOF'
[MIG] module_name: Migrate from X.0 to Y.0

Changes:
- Applied version-specific changes [1]
- Updated deprecated APIs [2]
- Fixed view syntax

Refs:
[1]: https://github.com/Vauxoo/odoo/commit/<commit_hash>
[2]: https://github.com/Vauxoo/odoo/commit/<commit_hash>
EOF
)"

# Push and create MR
git push -u origin HEAD
glab mr create --fill --yes
```

**MR title format:** `[MIG] module_name: Migrate from X.0 to Y.0`

### Commit Message Format with References

The commit message should follow this structure with **numbered references** and **GitHub URLs**:

```
[MIG] module_name: Migrate from X.0 to Y.0

Changes:
- Renamed field `deprecated` to `active` in account.account [1]
- Replaced `map_accounts(dict)` with `map_account(account)` [2]
- Applied tree→list view syntax [3]
- Migrated POS from Registries.Component.extend to OWL patch() [4]
- Updated asset bundle point_of_sale.assets → point_of_sale._assets_pos [5]
- Applied prefer-env-translation (self.env._ instead of _) [6]
- Pre-commit fixes applied

Refs:
[1]: https://github.com/odoo/odoo/commit/d44f9247
[2]: https://github.com/odoo/odoo/commit/be0a56ea
[3]: https://github.com/odoo/odoo/commit/4d5e84f7
[4]: https://github.com/odoo/odoo/commit/b119cca3
[5]: https://github.com/odoo/odoo/commit/c313f591
[6]: https://github.com/odoo/odoo/commit/b794f0f3
```

**Guidelines:**
- **Add [N]** suffix only to changes that have a verified Odoo commit reference
- **Reuse numbers** if multiple changes come from the same commit
- **Changes without references** (like pre-commit fixes, version bump) don't get a number
- **Order references** by first appearance in the Changes list
- **Always use full GitHub URL**: `https://github.com/odoo/odoo/commit/<8-char-hash>`
- **Hash length**: Always use **8 characters** for commit hashes
- If no reference commit found, omit from Refs section (don't add placeholder)

## Response Format

### Summary
- Module and version range (X.0 → Y.0)
- Migration command executed
- Main errors detected (categorized)

### Changes Made
- Fixes applied with version patterns
- Pre-commit validations passed
- Commits created

### Current Status
- Test results (passing/failing)
- MR URL (if created)
- Remaining issues (if any)

## Additional Resources

### References

| File | When to use | Search patterns |
|------|-------------|-----------------|
| `version_critical_changes.md` | Breaking changes | `grep "## v{VERSION}"` |
| `change_dependencies.md` | Fix order | `grep -A20 "## v{VERSION}"` |
| `common_issues.md` | Troubleshooting | `grep -i "{error_type}"` |
| `fix_patterns.md` | Manual fix patterns | `grep "## v{VERSION}"` |
| `debugging_strategies.md` | Investigation | `grep "### Step"` |
| `migration_tools.md` | Commands | `grep "###"` |

## Context7 Integration (Optional)

When local references and OCA Wiki don't cover a specific error, use Context7 for up-to-date documentation. If Context7 is unavailable (no connection, service error), continue with the next source without blocking.

### Dynamic Library Discovery

Context7 continuously indexes new libraries. **Always use `resolve-library-id` first** to discover available documentation for your target version.

### Workflow

1. **Resolve library ID dynamically:**
   ```
   resolve-library-id(libraryName="odoo 18", query="API changes fields methods")
   ```
   This finds the best matching library for Odoo 18.0 documentation.

2. **Query documentation with resolved ID:**
   ```
   query-docs(libraryId="/websites/odoo_18_0_developer", query="tree to list view migration")
   ```

3. **For OpenUpgrade scripts:**
   ```
   resolve-library-id(libraryName="openupgrade", query="migration scripts odoo")
   query-docs(libraryId="<resolved-id>", query="account module migration script")
   ```

### When to Use
1. Local `references/` files don't cover the error
2. OCA Migration Wiki doesn't have the specific pattern
3. Need to validate API changes against official docs
4. Looking for OpenUpgrade migration scripts
5. Migrating to a version not covered in local references

### Known Library IDs (as of 2025-01)

These are known IDs, but **always use resolve-library-id** to get current availability:

| Target | Library ID | Notes |
|--------|------------|-------|
| Odoo 19.0 | `/websites/odoo_19_0_developer` | ~3900 snippets |
| Odoo 18.0 | `/websites/odoo_18_0_developer` | ~1500 snippets |
| Odoo 12.0 | `/websites/odoo_12_0_developer` | ~800 snippets |
| OpenUpgrade | `/tickernelz/openupgrade` | ~1400 snippets |

**Note:** New versions may be indexed at any time. If migrating to v13-17, check availability with resolve-library-id.

## Critical Principles

**NEVER Remove or Simplify XPaths**
When an xpath fails, you MUST investigate the target version structure before making changes.
Removing functionality is NOT a valid fix. See "Mandatory Rules for View/XPath Changes" section.

**Execute, Don't Assume**
Run `odoo-mig migrate` to start migration. Do not wait for pre-existing logs.

**Validate Every Change**
Run `pre-commit-vauxoo` after each fix. Commit only validated code.

**Version-Aware Migration**
Check `version_critical_changes.md` for ALL versions in range before investigating.

**Never Invent Solutions**
Base fixes on Community/Enterprise/OCA source code and documented patterns.

**Complete the Cycle**
Migration is not done until MR is created. Execute full workflow autonomously.

## When to Stop

Stop iterating when:
- All tests pass AND MR created successfully
- Functional decision needed (ambiguous business logic)
- Repeated failures suggest architectural issue
- Prerequisites missing (tools not installed)

Report current state, changes applied, and MR URL or blockers.

## Example Workflow

```
1. User: "Migrate my_module to 18.0"

2. Verify prerequisites
   → odoo-mig: installed
   → pre-commit-vauxoo: installed
   → glab: configured

3. Detect source version (if not specified)
   → grep version from ./my_module/__manifest__.py
   → Found: "17.0.1.0.0" → Source version: 17.0

4. Execute migration
   → odoo-mig migrate ./my_module --from 17.0 --to 18.0 2>&1 | tee migration.log

5. Analyze log
   → 3 errors: tree→list views, deprecated method, xpath error

5b. XPath error found (MANDATORY INVESTIGATION)
   → ERROR: Element 'td[@name="td_taxes"]' cannot be located

   Investigation Checklist:
   - [x] Original purpose: Hide taxes column in sale report
   - [x] Searched target: grep -rn "td.*name=" ~/instance/odoo/addons/sale/report/
   - [x] Found equivalent: td[@name="td_product_taxes"] in ir_actions_report_templates.xml:235
   - [x] Mapping documented: td_taxes → td_product_taxes

   Applied fix:
   → Changed xpath from td[@name="td_taxes"] to td[@name="td_product_taxes"]
   → Functionality preserved: taxes column still hidden

   INVALID approach (would require user approval):
   → Removing the entire xpath
   → Simplifying the report template

6. Read version_critical_changes.md for v18.0
   → tree→list is documented change

7. Apply fixes
   → Fix 1: tree→list in views
   → pre-commit-vauxoo ✓
   → Fix 2: deprecated method
   → pre-commit-vauxoo ✓

8. Run tests
   → All passing

9. Document changes with commit references (odoo-commit-finder)
   → Analyze git diff to identify significant changes:
     - tree→list view syntax change
     - td_taxes→td_product_taxes xpath update

   → Search for reference commits:
     > "busca el commit de tree changed to list in views"
     → Found: abc123def [IMP] views: tree→list migration (odoo/odoo#198765)

     > "dame el commit del cambio de td_taxes a td_product_taxes"
     → Found: 789xyz456 [REF] sale: rename report elements (odoo/odoo#201234)

   → Collected refs with numbered format and GitHub URLs:
     [1]: https://github.com/Vauxoo/odoo/commit/abc123def
     [2]: https://github.com/Vauxoo/odoo/commit/789xyz456

10. Create MR with references
    → git commit -m "[MIG] my_module: Migrate from 17.0 to 18.0

    Changes:
    - Applied v18.0 tree→list conversion [1]
    - Updated xpath td_taxes→td_product_taxes [2]
    - Pre-commit fixes applied

    Refs:
    [1]: https://github.com/Vauxoo/odoo/commit/abc123def
    [2]: https://github.com/Vauxoo/odoo/commit/789xyz456"

    → git push && glab mr create --fill --yes
    → MR URL: https://git.vauxoo.com/...

11. Report:
    "Migrated my_module 17.0→18.0:
    - Executed odoo-mig migrate
    - Applied v18.0 tree→list conversion
    - Fixed deprecated API calls
    - All tests passing
    - Commit includes 2 Odoo reference commits
    - MR created: https://git.vauxoo.com/..."
```
