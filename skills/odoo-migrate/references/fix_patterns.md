# Fix Patterns for Manual Migration

Patterns for errors that `odoo-mig` cannot automatize. Apply these when encountering specific post-migration errors.

---

## v16.0 → v17.0

### attrs → Python Expressions

**Error indicator:** `ParseError` in XML views, `attrs` attribute deprecated

**Reference:** https://github.com/odoo/odoo/pull/104741

**Pattern:**

```xml
<!-- OLD -->
<field name="x" attrs="{'invisible': [('state', '=', 'draft')]}"/>
<field name="y" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
<field name="z" attrs="{'required': [('field_x', '=', True)]}"/>

<!-- NEW -->
<field name="x" invisible="state == 'draft'"/>
<field name="y" readonly="state != 'draft'"/>
<field name="z" required="field_x"/>
```

**Conversion rules:**

| Domain | Python Expression |
|--------|-------------------|
| `[('x', '=', 'y')]` | `x == 'y'` |
| `[('x', '!=', 'y')]` | `x != 'y'` |
| `[('x', 'in', [a,b])]` | `x in ['a','b']` |
| `[('a', '=', 'x'), ('b', '=', 'y')]` | `a == 'x' and b == 'y'` |
| `['|', ('a', '=', 'x'), ('b', '=', 'y')]` | `a == 'x' or b == 'y'` |

**Tool:** OCA `views_migration_17` module for automated conversion.

---

### Hook Signatures

**Error indicator:** `TypeError` in module hooks, wrong number of arguments

**Reference:** https://github.com/odoo/odoo/commit/b4a7996e967621aa090dc80346e6c3ef1d032dcf

**Pattern:**

```python
# OLD (v16.0 and earlier)
def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # ... do something ...

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # ... do something ...

# NEW (v17.0+)
def post_init_hook(env):
    # ... do something ...

def uninstall_hook(env):
    # ... do something ...
```

**Files to check:** `__init__.py` in module root.

---

## v17.0 → v18.0

### tree → list Views

**Error indicator:** View type errors, XML parsing issues with `<tree>`

**Reference:** https://github.com/odoo/odoo/pull/159909

**Pattern:**

```xml
<!-- OLD -->
<tree string="Records">
    <field name="name"/>
</tree>

<!-- NEW -->
<list string="Records">
    <field name="name"/>
</list>
```

```python
# OLD
action = {'type': 'ir.actions.act_window', 'view_mode': 'tree,form'}

# NEW
action = {'type': 'ir.actions.act_window', 'view_mode': 'list,form'}
```

**Automated tool:**
```bash
odoo-bin upgrade_code --addons-path /path/to/module
```

**SQL for database update (if needed):**
```sql
UPDATE ir_ui_view
SET arch_db = REPLACE(arch_db, '<tree', '<list')
WHERE arch_db LIKE '%<tree%';

UPDATE ir_ui_view
SET arch_db = REPLACE(arch_db, '</tree>', '</list>')
WHERE arch_db LIKE '%</tree>%';
```

**Note:** Keep XML-IDs with 'tree' in name for backward compatibility.

---

## v18.0 → v19.0

### Domain API

**Error indicator:** `ImportError` for `odoo.osv.expression`, domain operations failing

**Reference:** https://github.com/odoo/odoo/pull/217708

**Pattern:**

```python
# OLD
from odoo.osv import expression

domain = expression.AND([domain1, domain2])
domain = expression.OR([domain1, domain2])
domain = expression.normalize_domain(domain)

# NEW
from odoo.fields import Domain

domain = Domain(domain1) & Domain(domain2)
domain = Domain(domain1) | Domain(domain2)
# Auto-normalized, no need for normalize_domain
```

**Search methods returning domains:**
```python
# OLD
def _search_custom_field(self, operator, value):
    return [('field', '=', 'value')]

# NEW
def _search_custom_field(self, operator, value):
    return Domain([('field', '=', 'value')])
```

---

### groups_id → group_ids

**Error indicator:** `FieldError` for `groups_id`, access control issues

**Reference:** https://github.com/odoo/odoo/pull/179354

**Affected models:**
- `res.users`
- `ir.ui.view`
- `ir.ui.menu`
- `ir.actions.*`
- `website.page.properties`

**Pattern:**

```python
# OLD
user.groups_id = [(4, group.id)]
view.groups_id = security_group

# NEW
user.group_ids = [(4, group.id)]
view.group_ids = security_group
```

```xml
<!-- OLD -->
<field name="groups_id"/>

<!-- NEW -->
<field name="group_ids"/>
```

**Files to check:** All Python and XML files referencing `groups_id`.

---

### SQL Constraints

**Error indicator:** Model loading error, constraint syntax error

**Reference:** https://github.com/odoo/odoo/pull/175783

**Pattern:**

```python
# OLD
_sql_constraints = [
    ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
]

# NEW
_sql_constraints = [
    models.Constraint('unique(name)', 'Name must be unique!'),
]
```

---

### Internal Variables

**Error indicator:** `AttributeError` for `_cr`, `_uid`, `_context`

**Pattern:**

```python
# OLD
cr = self._cr
uid = self._uid
context = self._context

# NEW
cr = self.env.cr
uid = self.env.uid
context = self.env.context
```

---

## Quick Search Commands

Find files needing each pattern:

```bash
# attrs (v17)
grep -r "attrs=" --include="*.xml" .

# Hook signatures (v17)
grep -r "def post_init_hook\|def uninstall_hook" --include="*.py" .

# tree views (v18)
grep -r "<tree\|</tree>" --include="*.xml" .

# Domain API (v19)
grep -r "from odoo.osv import expression\|expression\.AND\|expression\.OR" --include="*.py" .

# groups_id (v19)
grep -r "groups_id" --include="*.py" --include="*.xml" .

# Internal vars (v19)
grep -r "self\._cr\|self\._uid\|self\._context" --include="*.py" .
```
