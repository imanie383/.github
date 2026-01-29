---
name: odoo-commit-finder
description: |
  Dynamic search tool for finding Odoo native commits that document ANY migration change.
  NOT limited to predefined changes - extracts keywords from ANY user description
  and builds appropriate git search commands dynamically.
  Use when user says "dame el commit", "find the commit", "busca el commit",
  "encuentra el commit de...", or needs to document migration changes with official references.
  Accepts ANY description: field renames, method changes, view modifications, API changes,
  attribute removals, model changes, deprecated features, new requirements, etc.
  Dynamically extracts identifiers, action verbs, and context from user input.
---

# Odoo Commit Finder

Dynamic search tool for finding native Odoo commits that document ANY migration change.

## Purpose

When migrating Odoo modules between versions, it's important to reference the official Odoo commits that introduced breaking changes. This skill **dynamically** searches the Odoo repository to find those commits based on **any description** the user provides - it is NOT limited to a predefined list of changes.

## Key Principle

**Check References → Extract → Build → Search → Refine**

**MANDATORY**: Always check the pre-verified references file FIRST before any git search.

This skill checks pre-verified references, extracts keywords from the user's natural language description, builds the appropriate git command, executes the search, and iteratively refines until the correct commit is found.

## Prerequisites

- Access to the Odoo repository at `~/instance/odoo`
- Git installed and configured
- **CRITICAL**: Access to the common references file (see below)

## ⚠️ MANDATORY FIRST STEP: Read Common References File

**BEFORE ANY GIT SEARCH**, you MUST read and check this file:

```
/home/odoo/instance/extra_addons/claude-code-vauxoo/plugins/odoo-migration-expert/skills/odoo-commit-finder/references/common_commit_references.md
```

This file contains **pre-verified commit references** for frequently encountered changes:
- Model attribute changes (`self._cr` → `self.env.cr`, `self._context` → `self.env.context`)
- Field renames (`deprecated` → `active`)
- Method changes (`map_accounts` → `map_account`)
- POS architecture changes (Registries → OWL patch)
- Translation patterns (`_()` → `self.env._()`)
- Asset bundle changes
- View syntax changes (`tree` → `list`, `attrs` removal)
- And more...

### Why This Is Mandatory

1. **Efficiency**: Pre-verified references save time and avoid unnecessary git searches
2. **Accuracy**: These references have been validated and are known to be correct
3. **Consistency**: Using the same references ensures consistent documentation across migrations

### When to Use Git Search

Only search with git commands when:
1. The change is **NOT found** in `common_commit_references.md`
2. You need to verify or get more details about a reference
3. You're looking for a very specific or unusual change not covered by common patterns

## Workflow

### Step 0: Check Common References File (MANDATORY)

**ALWAYS execute this step first, before any other action:**

```bash
# Read the common references file
cat /home/odoo/instance/extra_addons/claude-code-vauxoo/plugins/odoo-migration-expert/skills/odoo-commit-finder/references/common_commit_references.md
```

Or use the Read tool to read the file contents.

**If the change is found in this file:**
- Use the reference directly
- Format the output according to Step 5 and Step 6
- Do NOT proceed with git searches

**If the change is NOT found:**
- Proceed to Step 1 and continue with git search

### Step 1: Receive Change Description

The user provides a hint about the change they need to document:
- Field rename (e.g., "deprecated renamed to active")
- Attribute removal (e.g., "string attribute removed from group in search view")
- Method change (e.g., "map_accounts changed to map_account")
- View syntax change (e.g., "tree element changed to list")

### Step 2: Extract Keywords

Parse the user's description to identify:
- **Primary terms**: The main subject (field name, method name, element name)
- **Action terms**: What happened (rename, remove, change, deprecate)
- **Context terms**: Where it happened (model name, view type, file type)

### Step 3: Execute Search

Search in `~/instance/odoo` using multiple strategies:

#### Strategy A: Search in Commit Messages (preferred for documented changes)
```bash
cd ~/instance/odoo && git log --all --oneline --grep="keyword1" --grep="keyword2" | head -20
```

Use `--all-match` to require all grep terms:
```bash
cd ~/instance/odoo && git log --all --oneline --grep="keyword1" --grep="keyword2" --all-match | head -20
```

#### Strategy B: Search in Code Changes (pickaxe - for finding when code was added/removed)
```bash
cd ~/instance/odoo && git log -S "search_term" --oneline --all | head -20
```

Filter by file type:
```bash
cd ~/instance/odoo && git log -S "search_term" --oneline --all -- "*.py" | head -20
cd ~/instance/odoo && git log -S "search_term" --oneline --all -- "*.xml" | head -20
```

### Step 4: Show Commit Details

Once a candidate commit is found, show full details:
```bash
cd ~/instance/odoo && git show <commit_hash> --stat | head -60
```

### Step 5: Format Output

Present the commit information in a structured format:

```
**Commit encontrado:**

**<short_hash>** - `<commit_title>`
- Autor: <author_name> <author_email>
- Fecha: <commit_date>
- PR: odoo/odoo#<pr_number>
- Task: <task_id>

Descripcion:
> <commit_body>

Archivos modificados: <file_count> files
```

### Step 6: Format References for Migration Commits

**CRITICAL**: When this skill is used to document migration changes (invoked by `odoo-migrate` or for MR documentation), format the output with **numbered references** pointing to **full GitHub URLs**.

#### Reference Format Rules

1. **In the Changes section**: Add `[N]` suffix to changes that have an associated commit reference
2. **In the Refs section**: Use numbered format with full GitHub URLs: `[N]: https://github.com/odoo/odoo/commit/<8-char-hash>`
3. **Always use 8-character hashes** for consistency and readability

#### Example Output Format

**CORRECT format** (use this):
```
Changes:
- Bump version to 19.0.1.0.0
- Replaced deprecated field `exclude_from_invoice_tab` with `display_type == 'product'` [1]
- Migrated POS JS from legacy Registries.Component.extend to OWL 2 patch() pattern [2]
- Updated asset bundle from point_of_sale.assets to point_of_sale._assets_pos [3]
- Applied tree→list view syntax (stock_move_line_views.xml) [4]
- Applied self.env._ for translations (prefer-env-translation) [5]

Refs:
[1]: https://github.com/odoo/odoo/commit/d8d47f9f
[2]: https://github.com/odoo/odoo/commit/b119cca3
[3]: https://github.com/odoo/odoo/commit/c313f591
[4]: https://github.com/odoo/odoo/commit/4d5e84f7
[5]: https://github.com/odoo/odoo/commit/b794f0f3
```

**INCORRECT format** (do NOT use this):
```
Refs:
- d8d47f9f [REF] accounting v16: exclude_from_invoice_tab merged into display_type
- b119cca3 [REF] point_of_sale, *: remove class and component registries
```

**Also INCORRECT** (missing references for changes):
```
Changes:
- Applied tree→list view syntax
- Applied self.env._ for translations
# ^^^ These changes SHOULD have references!
```

#### Guidelines for Numbered References

1. **Only add [N]** to changes that have a verified commit reference
2. **Reuse the same number** if multiple changes come from the same commit
3. **Changes without references** (like version bump, pre-commit fixes) don't get a number
4. **Order references** by first appearance in the Changes list
5. **Always use full GitHub URL**: `https://github.com/odoo/odoo/commit/<8-char-hash>`
6. **Search for ALL changes**: Don't skip changes - every code modification should have a reference if one exists
7. **Check common_commit_references.md first**: Use pre-verified references when available

#### Finding References for ALL Changes

When documenting migration commits, you MUST find references for every significant change:

| Change Type | Must Have Reference | Example |
|-------------|--------------------|---------|
| Field renames/deprecations | YES | deprecated → active |
| Method changes | YES | map_accounts → map_account |
| View syntax changes | YES | tree → list |
| JS architecture changes | YES | Registries → OWL |
| Asset bundle changes | YES | point_of_sale.assets → _assets_pos |
| Translation pattern | YES | _() → self.env._() |
| Model attribute changes | YES | self._context → self.env.context |
| Version bump | NO | 15.0 → 19.0 |
| Pre-commit auto-fixes | NO | formatting, imports |

**Process:**
1. List all changes from `git diff`
2. For each change, check `common_commit_references.md`
3. If not found, search with git commands
4. Document ALL found references in the commit

## Search Patterns Reference Guide

These are **example patterns** - the skill dynamically builds commands for ANY change type:

| Change Type | Suggested Strategy | When to Use |
|-------------|-------------------|-------------|
| Field renamed | `--grep="rename" --grep="{field}"` | Documented renames with clear commit messages |
| Field removed | `--grep="remove" --grep="{field}"` | Fields dropped from models |
| Attribute changed | `--grep="{attr}" --grep="attribute"` | XML/view attribute changes |
| Method deprecated | `--grep="deprecat" --grep="{method}"` | API deprecations |
| Method removed/refactored | `-S "def {method}" -- "*.py"` | Methods removed without "rename" in commit message |
| Code pattern changed | `-S "{exact_code}"` | When you know the exact old/new code |
| View element changed | `-S "{element}" -- "*.xml"` | XML tag/element changes |
| Model restructured | `--grep="{model}" --grep="refactor\|change"` | Major model changes |
| Import changed | `-S "from {module}"` | Module/import restructuring |
| Decorator changed | `-S "@{decorator}"` | Decorator changes in Python |
| SQL/Query changed | `-S "{table_name}" -- "*.py"` | Database-related changes |

**Note**: These are starting points. The skill will adapt the search based on results.

## Dynamic Search Strategy

This skill is NOT limited to predefined changes. It dynamically extracts keywords from ANY user description and builds the appropriate git search command.

### Keyword Extraction Algorithm

From the user's description, extract:

1. **Identifiers**: Field names, method names, class names, XML elements, attributes
   - Look for: snake_case terms, CamelCase terms, quoted strings, XML-like tags
   - Examples: `deprecated`, `company_id`, `map_accounts`, `<tree>`, `string`

2. **Action verbs**: What happened to the identifier
   - Rename/renamed → search with `rename`, `change`
   - Remove/removed/delete → search with `remove`, `drop`
   - Deprecate/deprecated → search with `deprecat` (partial match)
   - Change/changed/modify → search with `change`, `update`
   - Add/added/new → search with `add`, `new`, `introduce`

3. **Context clues**: Where the change occurred
   - Model names: `account.account`, `res.partner`, `sale.order`
   - File types: Python (`.py`), XML (`.xml`), JS (`.js`)
   - Module names: `account`, `sale`, `stock`, `purchase`

### Search Command Builder

Based on extracted keywords, build commands dynamically:

**For text/concept changes (renames, removals, deprecations):**
```bash
cd ~/instance/odoo && git log --all --oneline --grep="{keyword1}" --grep="{keyword2}" --all-match | head -30
```

**For code changes (when searching for specific code patterns):**
```bash
cd ~/instance/odoo && git log -S "{exact_term}" --oneline --all -- "*.{ext}" | head -30
```

**For regex patterns in code:**
```bash
cd ~/instance/odoo && git log -G "{regex_pattern}" --oneline --all | head -30
```

### Iterative Search Process

1. **First attempt**: Use the most specific keywords from user description
2. **If no results**: Broaden search by removing action verbs, keep only identifiers
3. **If too many results**: Add more context (module name, file type filter)
4. **If still nothing**: Try pickaxe search (`-S`) with the exact term
5. **Last resort**: Search with partial/truncated keywords

### Examples of Dynamic Extraction

| User Says | Extracted Keywords | Command Built |
|-----------|-------------------|---------------|
| "el campo deprecated se renombró a active" | `deprecated`, `active`, `rename` | `git log --grep="deprecated" --grep="rename" --all-match` |
| "quitaron el atributo string de group en search" | `string`, `group`, `remove`, `attribute` | `git log --grep="string" --grep="attribute" --grep="remove"` |
| "changed tree to list in views" | `tree`, `list` | `git log -S "<tree" -- "*.xml"` then `git log --grep="tree" --grep="list"` |
| "method _compute_x was renamed" | `_compute_x`, `rename` | `git log -S "_compute_x" -- "*.py"` |
| "fiscal position map_accounts" | `map_accounts`, `fiscal` | `git log --grep="map_accounts"` or `git log -S "map_accounts"` |
| "map_accounts(dict) renamed to map_account" | `map_accounts`, `map_account` | `git log -S "map_accounts" -- "*.py"` (pickaxe for method removal) |
| "company_id changed to Many2many" | `company_id`, `company_ids`, `Many2many` | `git log --grep="company_id" --grep="many2many" -i` |

### Handling Ambiguous Requests

If the user's description is vague:
1. Ask for clarification: "¿Podrías especificar el nombre del campo/método/elemento?"
2. Suggest possible interpretations
3. Start with a broad search and present multiple candidate commits

## Example Sessions

### Example 1: Field Rename with Clear Commit Message

**User input:**
> "dame el commit del cambio de deprecated a active en account.account"

**Search execution:**
```bash
cd ~/instance/odoo && git log --all --oneline --grep="deprecated" --grep="active" --all-match | head -20
```

**Result:**
```
d44f9247 [IMP] account,*: account.deprecated rename
```

**Get details:**
```bash
cd ~/instance/odoo && git show d44f9247 --stat | head -40
```

**Formatted output:**
```
**Commit encontrado:**

**d44f9247** - `[IMP] account,*: account.deprecated rename`
- Autor: Habib (ayh) <ayh@odoo.com>
- Fecha: Thu Dec 26 02:11:58 2024
- PR: odoo/odoo#205191
- Task: 4422708

Descripcion:
> Accounts (account.account) has a boolean field called `deprecated`.
> This commit replaces that field with odoo's standard active field,
> and inverts the boolean logic.

Archivos modificados: 33 files
```

**For migration documentation (when used by odoo-migrate):**
```
Changes:
- Renamed field `deprecated` to `active` in account.account (inverted boolean logic) [1]

Refs:
[1]: https://github.com/odoo/odoo/commit/d44f9247
```

### Example 2: Method Removal (map_accounts → map_account)

**User input:**
> "Fiscal_position: map_accounts(dict) renamed to map_account"

**Keyword extraction:**
- Primary identifiers: `map_accounts`, `map_account`
- Context: `fiscal_position`, `fiscal`
- Action: This is actually a removal/refactor, not a simple rename

**Search strategy:**
Initial grep search may not find results since the commit message doesn't mention "rename":
```bash
cd ~/instance/odoo && git log --all --oneline --grep="map_accounts" --grep="rename" --all-match | head -20
# No results
```

Broaden to search just the method name:
```bash
cd ~/instance/odoo && git log --all --oneline --grep="map_accounts" | head -20
# Returns unrelated commits
```

Use pickaxe to find code changes:
```bash
cd ~/instance/odoo && git log -S "map_accounts" --oneline --all -- "*.py" | head -30
```

**Result:**
```
be0a56ea [REF] account,point_of_sale: cache line mapping to reduce complexity
c04065ab [IMP] accounting v9. Yeeeeaah
```

**Get details:**
```bash
cd ~/instance/odoo && git show be0a56ea --stat | head -60
```

**Verify the change:**
```bash
cd ~/instance/odoo && git show be0a56ea | grep -A5 -B5 "map_account" | head -50
```

**Formatted output:**
```
**Commit encontrado:**

**be0a56ea** - `[REF] account,point_of_sale: cache line mapping to reduce complexity`
- Autor: william-andre <wan@odoo.com>
- Fecha: Tue Apr 23 14:57:48 2024 +0200
- PR: odoo/odoo#162996
- Signed-off-by: Laurent Smet (las) <las@odoo.com>

Descripcion:
> An optimization was done in PoS to avoid recomputing multiple times the
> result of the mapping of one tax to another. Instead of doing that locally
> in the PoS, we can actually benefit from that in all the modules using
> fiscal positions, as well for the accounts.
> The functions calling `map_account` and `map_tax` are indeed often calling
> these inside of loops, multiplying the algorithmic complexity of these
> methods by the number of mappings for the fiscal position.

Cambio relevante:
> El método `map_accounts(accounts)` que recibía un diccionario fue **eliminado**.
> Ahora se debe usar `map_account(account)` individualmente:
>
> # ANTES (eliminado)
> def map_accounts(self, accounts):
>     """ Receive a dictionary having accounts in values... """
>
> # AHORA (usar directamente en comprehension)
> {key: fiscal_pos.map_account(account) for key, account in accounts.items()}

Archivos modificados: 6 files
```

**For migration documentation (when used by odoo-migrate):**
```
Changes:
- Replaced `map_accounts(dict)` with `map_account(account)` in fiscal position [1]

Refs:
[1]: https://github.com/odoo/odoo/commit/be0a56ea
```

**Key learning:** When a method is removed/refactored rather than renamed, the commit message may not contain "rename". Use pickaxe (`-S`) to find code changes directly.

## Tips for Effective Searching

### General Tips
1. **Start broad, then narrow**: Begin with fewer keywords, add more if too many results
2. **Use partial words**: `deprecat` matches both `deprecated` and `deprecation`
3. **Check related commits**: Often changes span multiple commits (data migration, code, views)
4. **Look at PR references**: The `Part-of:` or `closes:` lines link to full PR discussions
5. **Enterprise commits**: Some changes are in enterprise repo, search there if not found in community

### Dynamic Search Tips
6. **Extract the core identifier first**: Focus on the field/method/element name before action words
7. **Try both strategies**: If `--grep` doesn't find it, try `-S` (pickaxe) and vice versa
8. **Use case-insensitive search** (`-i`) for terms that might vary in capitalization
9. **Filter by module path**: Add `-- "addons/{module}/*"` to narrow results
10. **Search by author**: If you know who typically makes certain changes, use `--author="{name}"`
11. **Date range filtering**: Use `--since="2024-01-01"` to limit to recent versions
12. **Combine with grep on output**: `git log ... | grep -i "{keyword}"` for post-filtering

### When Nothing Is Found
- Try synonyms: `remove` ↔ `drop` ↔ `delete`, `rename` ↔ `change` ↔ `move`
- Search for the old AND new value separately
- Look in enterprise repo: `~/instance/enterprise`
- Check if the change was part of a larger refactor (search for the module name)
- Ask the user for more context or the exact code that changed
