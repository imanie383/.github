# Migration Tools Reference

All commands for migration workflow.

---

## odoo-mig

Primary migration tool.

```bash
# Execute migration
odoo-mig migrate /path/to/module --from X.0 --to Y.0 2>&1 | tee migration.log
```

---

## Automated Version Tools

| Version | Tool | Command |
|---------|------|---------|
| 11.0 | 2to3 | `2to3 -wnj4 --no-diffs .` |
| 17.0 | OCA views_migration_17 | Install module, run migration |
| 18.0 | upgrade_code | `odoo-bin upgrade_code --addons-path <path>` |

---

## Testing

### Standard Test Cycle

```bash
# Drop and recreate database
dropdb odoo_test 2>/dev/null || true
createdb odoo_test

# Run tests
odoo-bin --database=odoo_test --test-enable -i module1,module2 --stop-after-init --log-level=test

# Test with update
odoo-bin --database=odoo_test --test-enable -u module1,module2 --stop-after-init --log-level=test
```

### Test Output Analysis

```bash
# Capture output
odoo-bin --database=odoo_test --test-enable -i module --stop-after-init 2>&1 | tee test.log

# Find errors
grep -i "error" test.log

# Count warnings
grep -i "warning" test.log | wc -l
```

### Useful Flags

| Flag | Purpose |
|------|---------|
| `--test-tags module_name` | Test specific modules |
| `--log-level=debug` | Increase verbosity |
| `--without-demo=all` | Skip demo data |

---

## Database Operations

```bash
# List databases
psql -l

# Drop/Create
dropdb database_name
createdb database_name

# Backup
pg_dump odoo_prod > backup_$(date +%Y%m%d).sql

# Restore
psql database_name < backup.sql
```

---

## pre-commit-vauxoo

Run after each fix to validate code style.

```bash
# Run validation
pre-commit-vauxoo

# Stage modified files
git add -u
```

---

## glab (GitLab CLI)

Create merge requests.

```bash
# Push and create MR
git push -u origin HEAD
glab mr create --fill --yes
```

---

## Quick Fixes

### Clear Cache

```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

### Update Module List

```bash
odoo-bin -d DB -u all --stop-after-init
```

### Rebuild Views

```python
# In odoo-bin shell
env['ir.ui.view'].search([])._check_xml()
```

### Force Database Reload

```bash
dropdb DB && createdb DB && pg_restore -d DB backup.dump
```

---

## Complete Migration Workflow

```bash
# 1. Execute migration
odoo-mig migrate ./module --from X.0 --to Y.0 2>&1 | tee migration.log

# 2. Fix errors (loop)
# - Apply fix
# - pre-commit-vauxoo
# - git add -u

# 3. Test
dropdb odoo_test 2>/dev/null || true
createdb odoo_test
odoo-bin --database=odoo_test --test-enable -i module --stop-after-init

# 4. Commit and create MR
git add -A
git commit -m "[MIG] module: Migrate from X.0 to Y.0"
git push -u origin HEAD
glab mr create --fill --yes
```
