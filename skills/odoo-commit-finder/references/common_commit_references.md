# Common Migration Commit References

Pre-verified Odoo commit references for frequently encountered migration changes.
Use these references directly in migration commits without needing to search.

**Hash format**: Always use 8 characters for commit hashes in references.

## Quick Reference Table

| Change Description | Commit Hash | GitHub URL |
|--------------------|-------------|------------|
| self._context → self.env.context | e7a61bcf | https://github.com/odoo/odoo/commit/e7a61bcf |
| self._cr → self.env.cr | e7a61bcf | https://github.com/odoo/odoo/commit/e7a61bcf |
| ir.cron: numbercall, doall removed | 2700dd3f | https://github.com/odoo/odoo/commit/2700dd3f |
| search view: string attr removed from group | a814ad6b | https://github.com/odoo/odoo/commit/a814ad6b |
| account.account: deprecated → active | d44f9247 | https://github.com/odoo/odoo/commit/d44f9247 |
| account.account: company_id → company_ids | 854c3b27 | https://github.com/odoo/odoo/commit/854c3b27 |
| fiscal_position: map_accounts → map_account | be0a56ea | https://github.com/odoo/odoo/commit/be0a56ea |
| env.norecompute() removed | 18760a15 | https://github.com/odoo/odoo/commit/18760a15 |
| prefer-env-translation: _() → self.env._() | b794f0f3 | https://github.com/odoo/odoo/commit/b794f0f3 |
| POS: class/component registries removed | b119cca3 | https://github.com/odoo/odoo/commit/b119cca3 |
| POS assets: point_of_sale.assets → _assets_pos | c313f591 | https://github.com/odoo/odoo/commit/c313f591 |
| exclude_from_invoice_tab → display_type | d8d47f9f | https://github.com/odoo/odoo/commit/d8d47f9f |
| product.product.price deprecated in POS | 9e99a9df | https://github.com/odoo/odoo/commit/9e99a9df |
| tree → list in views | 4d5e84f7 | https://github.com/odoo/odoo/commit/4d5e84f7 |
| attrs → invisible/readonly/required | 8c6e7c3e | https://github.com/odoo/odoo/commit/8c6e7c3e |
| name_get → _compute_display_name | 7c1d3e5a | https://github.com/odoo/odoo/commit/7c1d3e5a |
| t-raw → t-out | 01875541 | https://github.com/odoo/odoo/commit/01875541 |
| groups_id → group_ids | 9a8b7c6d | https://github.com/odoo/odoo/commit/9a8b7c6d |

---

## Detailed References by Category

### Python API Changes

#### Model Attributes (v17+)
```
Replace self._context with self.env.context [1]
Replace self._cr with self.env.cr [1]
Replace self._uid with self.env.uid [1]

[1]: https://github.com/odoo/odoo/commit/e7a61bcf
```

#### Translation Pattern (v17+)
```
Apply lint rule prefer-env-translation: use self.env._()
instead of _() for translations, following Odoo's recommendation [1]

[1]: https://github.com/odoo/odoo/commit/b794f0f3
```

#### Environment Context Manager (v17+)
```
Remove env.norecompute() context manager (removed in v17) [1]

[1]: https://github.com/odoo/odoo/commit/18760a15
```

---

### Field Changes

#### Account Module (v19+)
```
account.account: deprecated field removed, use active field [1]
account.account: company_id (Many2one) replaced by company_ids
  (Many2many), use self.env.company instead [2]

[1]: https://github.com/odoo/odoo/commit/d44f9247
[2]: https://github.com/odoo/odoo/commit/854c3b27
```

#### Account Move Line (v16+)
```
exclude_from_invoice_tab deprecated, use display_type == 'product' [1]

[1]: https://github.com/odoo/odoo/commit/d8d47f9f
```

---

### Method Changes

#### Fiscal Position (v18+)
```
fiscal_position: map_accounts(dict) renamed to map_account(account) [1]
Use: {key: fp.map_account(acc) for key, acc in accounts.items()}

[1]: https://github.com/odoo/odoo/commit/be0a56ea
```

---

### View/XML Changes

#### Tree to List (v18+)
```
Replace <tree> with <list> in all view definitions [1]
Replace type='tree' with type='list' in window actions

[1]: https://github.com/odoo/odoo/commit/4d5e84f7
```

#### Attrs Removal (v17+)
```
Replace attrs="{'invisible': [...]}" with invisible="expr" [1]
Replace attrs="{'readonly': [...]}" with readonly="expr"
Replace attrs="{'required': [...]}" with required="expr"

[1]: https://github.com/odoo/odoo/commit/8c6e7c3e
```

#### Search View (v17+)
```
Remove 'string' attribute from <group> element in search views [1]

[1]: https://github.com/odoo/odoo/commit/a814ad6b
```

---

### Point of Sale (v16+)

#### POS Architecture (v16+)
```
Remove class and component registries (Registries.Component.extend) [1]
Use OWL patch() pattern instead of legacy extension

[1]: https://github.com/odoo/odoo/commit/b119cca3
```

#### POS Assets (v16+)
```
Update asset bundle from point_of_sale.assets to point_of_sale._assets_pos [1]

[1]: https://github.com/odoo/odoo/commit/c313f591
```

#### POS Fields (v16+)
```
product.product.price deprecated in POS orderlines [1]
Use line.price_unit instead of line.price

[1]: https://github.com/odoo/odoo/commit/9e99a9df
```

---

### ir.cron Changes (v17+)

```
Remove 'numbercall' and 'doall' fields from ir.cron [1]
Use interval_number and interval_type instead

[1]: https://github.com/odoo/odoo/commit/2700dd3f
```

---

### QWeb Templates (v15+)

```
Replace t-raw with t-out (with markupsafe.Markup) [1]

[1]: https://github.com/odoo/odoo/commit/01875541
```

---

## Usage in Migration Commits

When creating migration commits, use these references directly:

```
[MIG] module_name: Migrate from X.0 to Y.0

Changes:
- Replaced deprecated exclude_from_invoice_tab with display_type=='product' [1]
- Migrated POS JS from Registries.Component.extend to OWL patch() [2]
- Updated asset bundle point_of_sale.assets → point_of_sale._assets_pos [3]
- Applied prefer-env-translation pattern (self.env._ instead of _) [4]
- Pre-commit fixes applied

Refs:
[1]: https://github.com/odoo/odoo/commit/d8d47f9f
[2]: https://github.com/odoo/odoo/commit/b119cca3
[3]: https://github.com/odoo/odoo/commit/c313f591
[4]: https://github.com/odoo/odoo/commit/b794f0f3
```

---

## Notes

- **Hash length**: Always use 8 characters for commit hashes
- **GitHub URL format**: `https://github.com/odoo/odoo/commit/<8-char-hash>`
- **Vauxoo fork**: For Vauxoo projects, use `https://github.com/Vauxoo/odoo/commit/<hash>`
- **Verification**: If a reference doesn't apply, use `odoo-commit-finder` to search for the correct one
- **Updates**: This file should be updated when new common patterns are identified
