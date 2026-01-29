# Change Dependencies Map

Optimal fix order to avoid rework. **Priority**: CRITICAL → HIGH → MEDIUM → LOW

---

## v19.0

| Change | Priority | Blocks | Order |
|--------|----------|--------|-------|
| _sql_constraints | **CRITICAL** | Model loading | **First** |
| groups_id→group_ids | HIGH | Access rights, menus, views | Early |
| self._cr/_uid/_context | HIGH | DB operations | Early |
| Domain API | HIGH | Domain ops, search methods | After imports |
| Search returns Domain | MEDIUM | Computed searchable fields | After Domain API |
| read_group split | MEDIUM | Reporting | Anytime |
| type='jsonrpc' | MEDIUM | Controllers | Anytime |
| Timezone (env.tz) | MEDIUM | Datetime ops | Anytime |
| toggle_active | LOW | Archive ops | Anytime |
| bypass_search_access | LOW | Field defs | Anytime |

---

## v18.0

| Change | Priority | Notes |
|--------|----------|-------|
| tree→list | HIGH | Run `odoo-bin upgrade_code` first, then manual Python, then tests |

---

## v17.0

| Change | Priority | Blocks | Notes |
|--------|----------|--------|-------|
| Module hooks (env) | **CRITICAL** | Module install | **Do first** |
| attrs→Python | HIGH | View inherit, domains | Base views → Inherited → Tests |
| name_get→_compute | MEDIUM | Display, searches | Add @api.depends |
| column_invisible | MEDIUM | Tree/list display | Only tree/list views |

---

## v16.0

| Change | Priority |
|--------|----------|
| flush() | MEDIUM |
| _rec_names_search | LOW |
| fields_view_get→get_view | MEDIUM |
| get_xml_id→get_external_id | LOW |

All can be done in parallel.

---

## v15.0

| Change | Priority |
|--------|----------|
| Assets→manifest | HIGH |
| t-raw→t-out | MEDIUM |

---

## v14.0

| Change | Priority |
|--------|----------|
| invisible/readonly static | MEDIUM |
| selection_add ondelete | MEDIUM |

---

## v13.0

| Change | Priority |
|--------|----------|
| Remove @api decorators | HIGH |
| sudo(user)→with_user | MEDIUM |

---

## v12.0

| Change | Priority |
|--------|----------|
| Date/Datetime native | MEDIUM |
| _parent_store | MEDIUM |

---

## v11.0

| Change | Priority |
|--------|----------|
| Python 3 conversion | **CRITICAL** |
| __openerp__→__manifest__ | **CRITICAL** |

Use `2to3` tool for both.

---

## v10.0

| Change | Priority |
|--------|----------|
| openerp→odoo | **CRITICAL** |
| New API | **CRITICAL** |

---

## Multi-Version Strategies

### 15.0 → 19.0

**Critical Path:**
1. Module hooks (17.0)
2. _sql_constraints (19.0)

**Batch 1 - High Impact:**
- groups_id→group_ids (19.0)
- self._cr/_uid/_context (19.0)
- attrs→Python (17.0)
- tree→list (18.0)

**Batch 2 - API Changes:**
- Domain API (19.0)
- flush() (16.0)
- name_get (17.0)
- Assets (15.0)

**Batch 3 - Polish:**
- All LOW priority items

### Common Paths

| Path | Critical First |
|------|----------------|
| 16.0→17.0 | hooks (17.0), then attrs |
| 17.0→18.0 | tree→list (automated) |
| 18.0→19.0 | _sql_constraints, then groups_id, Domain API |

---

## Fix Order Rules

**Always first:**
1. Module hooks (v17.0+)
2. _sql_constraints (v19.0+)
3. Import changes (v10.0, v11.0)

**Then:**
1. High-impact view changes (attrs, tree→list)
2. Pervasive code changes (self._cr, groups_id)
3. Specific API changes

**Last:**
1. LOW priority optimizations
2. Tests
3. Docs

---

## Avoid Circular Issues

- Parents before inherited views (attrs)
- Import changes before usage (Domain API)
- Models before views
