# Version-Specific Critical Changes

Breaking changes per version. Check `fix_patterns.md` for detailed code patterns.

## Quick Lookup

| Ver | Python | Key Changes |
|-----|--------|-------------|
| 19.0 | 3.10+ | groups_id→group_ids, _cr/_uid/_context, Domain API, SQL constraints |
| 18.0 | 3.8+ | tree→list |
| 17.0 | 3.8+ | attrs→Python, name_get→_compute_display_name, hooks(env) |
| 16.0 | 3.7+ | flush()→flush_model(), _rec_names_search |
| 15.0 | 3.7+ | Assets in manifest, t-raw→t-out |
| 14.0 | 3.7+ | invisible/readonly static, selection_add ondelete |
| 13.0 | 3.6+ | Remove @api decorators, sudo(user)→with_user() |
| 12.0 | 3.6+ | Date/Datetime native objects |
| 11.0 | 3.5+ | Python 3, __openerp__→__manifest__ |
| 10.0 | 3.5+ | openerp→odoo imports |

---

## v19.0

| Change | Details | Ref |
|--------|---------|-----|
| groups_id→group_ids | res.users, ir.ui.view, ir.ui.menu, ir.actions.* | [#179354](https://github.com/odoo/odoo/pull/179354) |
| Internal vars | `self._cr`→`self.env.cr`, `self._uid`→`self.env.uid`, `self._context`→`self.env.context` | - |
| Domain API | `expression.AND([])` → `Domain() & Domain()` | [#217708](https://github.com/odoo/odoo/pull/217708) |
| SQL constraints | `('name', 'UNIQUE(x)', 'msg')` → `models.Constraint('unique(x)', 'msg')` | [#175783](https://github.com/odoo/odoo/pull/175783) |
| Timezone | `pytz.timezone()` → `self.env.tz` | [#221541](https://github.com/odoo/odoo/pull/221541) |
| auto_join | `auto_join=True` → `bypass_search_access=True` | [#219627](https://github.com/odoo/odoo/pull/219627) |
| read_group | Internal: `_read_group()`, Public: `formatted_read_group()` | [#163300](https://github.com/odoo/odoo/pull/163300) |
| Controllers | `type='json'` → `type='jsonrpc'` | [#183636](https://github.com/odoo/odoo/pull/183636) |
| Search methods | Return `Domain([...])` not `[...]` | [4f0d467](https://github.com/odoo/odoo/commit/4f0d4670ed) |
| toggle_active | → `action_archive()` or `action_unarchive()` | [#183691](https://github.com/odoo/odoo/pull/183691) |
| SUPERUSER_ID | Import from `odoo.api` not `odoo` | [d6a955f](https://github.com/odoo/odoo/commit/d6a955f10483) |
| Testing | Demo data NOT loaded by default, native fake models | - |

---

## v18.0

| Change | Details | Ref |
|--------|---------|-----|
| tree→list | `<tree>` → `<list>`, `type='tree'` → `type='list'` | [#159909](https://github.com/odoo/odoo/pull/159909) |

**Tool:** `odoo-bin upgrade_code --addons-path <path>`

---

## v17.0

| Change | Details | Ref |
|--------|---------|-----|
| attrs deprecated | `attrs="{'invisible': [...]}"` → `invisible="expr"` | [#104741](https://github.com/odoo/odoo/pull/104741) |
| name_get | → `_compute_display_name` with `@api.depends` | [#122085](https://github.com/odoo/odoo/pull/122085) |
| Module hooks | `(cr, registry)` → `(env)` | [b4a7996](https://github.com/odoo/odoo/commit/b4a7996e9676) |
| Tree views | `invisible="1"` → `column_invisible="1"` | - |
| get_resource_path | → `file_path` | - |

**Tool:** OCA `views_migration_17` module

---

## v16.0

| Change | Details | Ref |
|--------|---------|-----|
| flush() | → `flush_model()` or `flush_recordset()`, `env.flush()` → `env.flush_all()` | - |
| _rec_names_search | Override variable instead of `name_search` method | [3155c3e](https://github.com/odoo/odoo/commit/3155c3e42558) |
| fields_view_get | → `get_view` | - |
| get_xml_id | → `get_external_id()` | - |

---

## v15.0

| Change | Details | Ref |
|--------|---------|-----|
| Assets | Move from XML to `__manifest__.py` `'assets': {...}` | - |
| QWeb | `t-raw` → `t-out` (with `markupsafe.Markup`) | [0187554](https://github.com/odoo/odoo/commit/01875541b1a) |
| JS modules | `.js` → `.esm.js` + `/** @odoo-module **/` | - |

---

## v14.0

| Change | Details |
|--------|---------|
| Views | `invisible=`, `readonly=` must be static (use `attrs` for dynamic) |
| Transient models | Need explicit ACLs |
| selection_add | Must add `ondelete=` for new values |
| Char fields | `size=` removed |

---

## v13.0

| Change | Details |
|--------|---------|
| Decorators | Remove `@api.multi`, `@api.returns`, `@api.one`, `@api.cr`, `@api.model_cr` |
| sudo | `sudo(user)` → `with_user(user)` |
| Computed fields | Must explicitly set `store=True` or `compute_sudo=True` |

---

## v12.0

| Change | Details |
|--------|---------|
| Date/Datetime | Return native Python objects, no `from_string` needed |
| _parent_store | No longer auto-computed |
| website_published | → computed field (stored: `is_published`) |

---

## v11.0

| Change | Details |
|--------|---------|
| Python 3 | Use `2to3 -wnj4 --no-diffs .` |
| __openerp__.py | → `__manifest__.py` |

---

## v10.0

| Change | Details |
|--------|---------|
| Imports | `from openerp` → `from odoo` |
| Old API | Removed, must use new API |

---

## References

- **OCA Wiki**: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-{VERSION}
- **OpenUpgrade**: https://github.com/OCA/OpenUpgrade
