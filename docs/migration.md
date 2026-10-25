# Migration Guide — Noxen

This document details migration steps, breaking changes (if any), and deprecations between Noxen versions.

---

## Migrating from v0.2.0 to v0.3.0

### Non-Breaking Additions
* **Date & Time Validation**: You can now mark string fields with `.date()`, `.time()`, or `.datetime()`.
  ```nox
  s.field_str("birth_date").date()
  s.field_str("created_at").datetime()
  ```
* **Sensitive Data Redaction**: Use `.secret()` on passwords or tokens. If validation fails, error payloads mask `actual` as `[REDACTED]`.
* **Flexible Unknown Fields**: Set `s.set_policy(POLICY_ALLOW)` if you want to preserve extra fields in `ValidatedData.get_extra_keys()`.
* **JSON Schema `$defs`**: Nested schemas are now extracted into `$defs` blocks and referenced using `{"$ref": "#/$defs/SubModel"}` according to Draft 2020-12.

### Behavioral Invariants
* All existing schemas from v0.1.0 and v0.2.0 continue to compile and behave identically.

---

## Migrating from v0.1.0 to v0.2.0

### Additions
* **Ecosystem Adapters**:
  - `http_adapter.nox` provides `json_422`, `json_200`, and `json_201` for `nox.http` and Aether.
  - `db_adapter.nox` provides `DbAdapter[T]` and `row_to_validated_data` for `nox.db.Row` and Nyx.
* **Aliases**:
  - `f.alias("jsonKey")` allows mapping between JSON naming conventions and Nox model fields.
* **Choices**:
  - `f.in_choices(["a", "b", "c"])` and `f.in_choices_int([1, 2, 3])`.
