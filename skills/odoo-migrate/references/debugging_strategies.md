# Migration Debugging Strategies

Investigation workflow for migration errors. For commands, see `migration_tools.md`.

---

## Log Error Indicators

```
ImportError: cannot import name 'X'        → Module structure changed
FieldError: Field 'X' does not exist       → Field removed/renamed
ParseError: Invalid XML                    → View syntax changed
ProgrammingError: column "x" does not exist → Database schema mismatch
WARNING: deprecated method 'X'             → API change
```

---

## Investigation Workflow

### Step 1: Categorize Error

| Type | Examples |
|------|----------|
| Import/Structure | Missing modules, broken imports, wrong paths |
| Model/Field | Missing fields, renamed models, changed relations |
| View/XML | Invalid syntax, wrong field refs, deprecated attrs |
| Data/Constraint | Data integrity, required fields, domain violations |
| API/Logic | Method signature changes, deprecated APIs |

### Step 2: Locate Source of Truth

**Import/Structure:**
1. `~/instance/odoo/addons/module_name/`
2. `~/instance/enterprise/module_name/`
3. `~/instance/extra_addons/module_name/`

**Field/Model:**
1. `grep -r 'field_name' ~/instance/odoo/addons/module_name/models/`
2. OpenUpgrade upgrade_analysis.txt
3. Enterprise source if applicable

**View/XML:**
1. `~/instance/odoo/addons/module_name/views/`
2. OCA wiki for deprecations
3. Working examples in target version

**API/Logic:**
1. `grep -r 'def method_name' ~/instance/odoo/`
2. OCA wiki for API changes
3. Replacement method or pattern

### Step 3: Compare and Fix

- **Field renamed** → Update all references (models, views, code)
- **Method changed** → Update calls with new signature
- **View syntax changed** → Update XML to new standards
- **Module moved** → Update import paths

---

## Debugging Commands

### Find Field Usage
```bash
grep -r "field_name" --include="*.py" --include="*.xml" .
```

### Find Method Definition
```bash
grep -r "def method_name" ~/instance/odoo/ ~/instance/enterprise/
```

### Check Module Manifest
```bash
cat ~/instance/odoo/addons/module_name/__manifest__.py
```

### Compare Module Structure
```bash
ls -la ~/instance/odoo/addons/module_name/
ls -la ./custom_module/
```

---

## Odoo Shell Investigation

```bash
odoo-bin shell --database=odoo_test
```

```python
>>> env['model.name'].search([])
>>> env['model.name']._fields.keys()
>>> env.ref('module.xml_id')
```

---

## Database Inspection

```bash
# Check table exists
psql odoo_test -c "\dt *table_name*"

# Check table structure
psql odoo_test -c "\d table_name"

# Find columns
psql odoo_test -c "SELECT column_name FROM information_schema.columns WHERE table_name='table_name'"

# Find XML ID
psql odoo_test -c "SELECT * FROM ir_model_data WHERE name='xml_id_name'"
```

---

## When to Search Web

After checking all local sources:
1. Search specific error message
2. Odoo GitHub issues
3. OCA GitHub for module migrations
4. Odoo forums

Verify web findings against local source code.
