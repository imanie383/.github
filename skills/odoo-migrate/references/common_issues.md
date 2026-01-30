# Common Migration Issues

General troubleshooting guide. For version-specific patterns, see `fix_patterns.md`.

---

## Field Errors

### "Field X does not exist" but exists in code

**Causes:** Field renamed in core | Inheritance broken | Dependency missing

**Fix:**
1. Check OpenUpgrade: `https://github.com/OCA/OpenUpgrade/blob/{VERSION}/odoo/addons/{MODULE}/upgrade_analysis.txt`
2. Update all references: models, views, domains, searches
3. Prevention: `grep -r "field_name" .` before migrating

### Field type mismatch

**Example:** `TypeError: Trying to assign Many2one to JSON field`

**Fix (migration script):**
```python
def migrate(cr, version):
    cr.execute("""
        UPDATE table SET json_field =
        json_build_object(old_many2one_id::text, 100.0)
        WHERE old_many2one_id IS NOT NULL
    """)
```

---

## View Errors

### View inheritance broken

**Cause:** Parent view structure changed

**Fix:**
1. Compare: `diff custom/view.xml ~/instance/odoo/addons/module/views/view.xml`
2. Update XPath selectors
3. Re-inherit from scratch if structure too different

---

## Import Errors

### Circular import

**Fix:**
```python
# Use lazy import inside method
def method(self):
    from .other_model import OtherModel
    OtherModel.do_something()
```

Check `__init__.py` order: dependencies first.

---

## Database Errors

### IntegrityError on constraints

**Fix duplicates:**
```python
def migrate(cr, version):
    cr.execute("""
        SELECT name, COUNT(*) FROM table
        GROUP BY name HAVING COUNT(*) > 1
    """)
    # Handle each duplicate (merge/delete/rename)
```

**Disable temporarily (last resort):**
```python
cr.execute("ALTER TABLE t DROP CONSTRAINT c")
# ... fix data ...
cr.execute("ALTER TABLE t ADD CONSTRAINT c ...")
```

---

## Test Errors

### Tests pass locally, fail in CI

| Cause | Fix |
|-------|-----|
| Demo data dependency | Create test data explicitly |
| Test order dependency | Make tests independent, reset in `setUp()` |
| Tracking enabled | `cls.env = cls.env(context={'tracking_disable': True})` |

### Fake models not loading (v19.0)

```python
from odoo.orm.model_classes import add_to_registry

@classmethod
def setUpClass(cls):
    add_to_registry(cls.registry, FakeModel)
    cls.registry._setup_models__(cls.env.cr, ["fake.model"])
    cls.registry.init_models(cls.env.cr, ["fake.model"], {"models_to_check": True})
    cls.addClassCleanup(cls.registry.__delitem__, "fake.model")
```

---

## Performance Issues

### Migration very slow

| Issue | Bad | Good |
|-------|-----|------|
| Large data | `for r in model.search([])` | SQL: `cr.execute("UPDATE...")` |
| N+1 queries | Loop with `.field_id.name` | Prefetch or SQL join |
| No commits | Process all at once | Batch + `cr.commit()` every 1000 |

**Batch processing:**
```python
def migrate(cr, version):
    offset, limit = 0, 1000
    while True:
        cr.execute("SELECT id FROM table OFFSET %s LIMIT %s", (offset, limit))
        if not cr.fetchall(): break
        # process batch
        cr.commit()
        offset += limit
```

---

## Error Categories

| Category | First Check | Then |
|----------|-------------|------|
| Import | `version_critical_changes.md` | Module structure |
| Field | OpenUpgrade upgrade_analysis.txt | Core source |
| View | `fix_patterns.md` | Compare with target |
| API | OCA wiki | Method signatures |
| Database | Migration script needed | Data cleanup |
| Constraint | Data duplicates | Disable/re-enable |

---

## When to Ask for Help

**Ask when:**
- Error persists after checking all refs
- No similar issues online
- Core behavior differs from docs
- Database corruption suspected

**Where:** Odoo Forum, OCA GitHub, Stack Overflow (tag: odoo)
