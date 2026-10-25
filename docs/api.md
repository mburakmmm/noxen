# API Reference — Noxen

This document provides a complete reference for all public classes, functions, methods, and constants exposed by Noxen.

---

## 1. Constants

### Presence Modes (`schema.nox` / `fields.nox`)
* `MODE_REQUIRED: int = 0`: Field must exist in the payload and must not be null.
* `MODE_REQUIRED_NULLABLE: int = 1`: Field must exist in the payload, but its value may be explicit JSON `null`.
* `MODE_OPTIONAL: int = 2`: Field may be omitted. If present, it must not be null.
* `MODE_OPTIONAL_NULLABLE: int = 3`: Field may be omitted, or present with a non-null or null value.

### Unknown Field Policies (`schema.nox` / `fields.nox`)
* `POLICY_FORBID: int = 0`: (Default) Any field in the payload not declared in the schema raises a validation error (`extra_field`).
* `POLICY_IGNORE: int = 1`: Unknown fields are silently ignored and not stored.
* `POLICY_ALLOW: int = 2`: Unknown fields are accepted and preserved in `ValidatedData.get_extra_keys()`.

### Coercion Modes (`schema.nox` / `fields.nox`)
* `COERCION_STRICT: int = 0`: (Default) Disallows implicit conversions (e.g. `"123"` will not be coerced to integer `123`).
* `COERCION_LAX: int = 1`: Safely coerces convertible strings to numbers/booleans and vice versa.

---

## 2. Core Classes

### `Schema` (`schema.nox`)
The root validation engine for structured data.

* `Schema(name: str)`: Initializes a new schema.
* `set_policy(policy: int) -> None`: Sets the unknown fields policy (`POLICY_FORBID`, `POLICY_IGNORE`, `POLICY_ALLOW`).
* `set_coercion(mode: int) -> None`: Sets strict or lax coercion (`COERCION_STRICT`, `COERCION_LAX`).
* `field_str(name: str) -> Field`: Declares a string field.
* `field_int(name: str) -> Field`: Declares an integer field.
* `field_float(name: str) -> Field`: Declares a floating point field.
* `field_bool(name: str) -> Field`: Declares a boolean field.
* `field_object(name: str, sub: Schema) -> Field`: Declares a nested object field.
* `field_list(name: str, item_kind: str) -> Field`: Declares an array of primitives (`"string"`, `"int"`, `"float"`, `"bool"`).
* `field_list_schema(name: str, item_schema: Schema) -> Field`: Declares an array of nested objects.
* `add_validator(fn: (ValidatedData) -> list[FieldError]) -> None`: Registers a cross-field custom validator callback.
* `validate(v: JsonValue) -> ValidationResult`: Validates an in-memory `JsonValue` tree.
* `validate_json(json_str: str) -> ValidationResult`: Parses and validates a JSON string.
* `to_json_schema() -> str`: Generates standard JSON Schema Draft 2020-12 specification with `$defs` and `$ref`.

### `Field` (`schema.nox` / `fields.nox`)
Fluent builder for configuring field rules and constraints.

* `alias(json_key: str) -> Field`: Maps external JSON keys to the model field name.
* `optional() -> Field`: Makes the field optional.
* `nullable() -> Field`: Allows explicit null values.
* `secret() -> Field`: Masks the field value as `[REDACTED]` in error reports.
* `default_s(v: str) -> Field`: Sets a string default (applies on missing fields).
* `default_i(v: int) -> Field`: Sets an integer default.
* `default_f(v: float) -> Field`: Sets a float default.
* `default_b(v: bool) -> Field`: Sets a boolean default.
* `min(v: float) / ge(v: float) -> Field`: Inclusive minimum numeric bound.
* `max(v: float) / le(v: float) -> Field`: Inclusive maximum numeric bound.
* `gt(v: float) -> Field`: Exclusive minimum numeric bound.
* `lt(v: float) -> Field`: Exclusive maximum numeric bound.
* `min_length(n: int) -> Field`: Minimum string character length.
* `max_length(n: int) -> Field`: Maximum string character length.
* `regex(pat: str) -> Field`: Regular expression constraint.
* `in_choices(opts: list[str]) -> Field`: Restricts string to allowed choices.
* `in_choices_int(opts: list[int]) -> Field`: Restricts integer to allowed choices.
* `min_items(n: int) -> Field`: Minimum collection items.
* `max_items(n: int) -> Field`: Maximum collection items.
* `email() -> Field`: Validates standard email address.
* `url() -> Field`: Validates absolute HTTP/HTTPS URL via `nox.url`.
* `uuid() -> Field`: Validates canonical 36-character UUID format.
* `date() -> Field`: Validates ISO 8601 calendar date (`YYYY-MM-DD`).
* `time() -> Field`: Validates ISO 8601 time (`HH:MM:SS` with optional timezone/fraction).
* `datetime() -> Field`: Validates ISO 8601 datetime (`YYYY-MM-DDTHH:MM:SS[Z]`).
* `describe(desc: str) -> Field`: Adds human-readable documentation description.

### `ModelSchema[T]` (`models.nox`)
Generic wrapper mapping raw validated data into strongly typed Nox classes.

* `ModelSchema[T](schema: Schema, factory: (ValidatedData) -> T)`
* `parse_json(json_str: str) -> Result[T]`: Parses JSON, validates, and hydrates typed instance.
* `validate(v: JsonValue) -> Result[T]`: Validates `JsonValue` and hydrates typed instance.

### `Result[T]` (`core.nox`)
Generic result container representing validation outcome.

* `is_ok: bool`: True if validation succeeded.
* `errors: list[FieldError]`: List of collected field errors on failure.
* `unwrap() -> T`: Returns the inner value or raises `ValidationError`.
* `unwrap_or(default_val: T) -> T`: Returns the inner value or fallback.
* `errors_json() -> str`: Returns serialized JSON array of errors.

### `ValidatedData` (`core.nox`)
Typed accessor container for successfully validated values.

* `get_str(k) -> str`, `get_opt_str(k) -> str | None`
* `get_int(k) -> int`, `get_opt_int(k) -> int | None`
* `get_float(k) -> float`, `get_opt_float(k) -> float | None`
* `get_bool(k) -> bool`, `get_opt_bool(k) -> bool | None`
* `get_object(k) -> ValidatedData`, `get_opt_object(k) -> ValidatedData | None`
* `get_list_str(k) -> list[str]`, `get_list_int(k) -> list[int]`, `get_list_float(k) -> list[float]`, `get_list_bool(k) -> list[bool]`
* `has(k) -> bool`, `is_null(k) -> bool`
* `has_extra(k) -> bool`, `get_extra(k) -> str`, `get_extra_keys() -> list[str]`

### `Serializer` (`serialization.nox`)
Streaming fluent builder for high-performance JSON serialization.

* `str(k, v)`, `opt_str(k, v)`
* `int(k, v)`, `opt_int(k, v)`
* `float(k, v)`, `opt_float(k, v)`
* `bool(k, v)`, `opt_bool(k, v)`
* `null(k)`
* `list_str(k, items)`, `list_int(k, items)`, `list_float(k, items)`, `list_bool(k, items)`
* `raw_json(k, json_text)`, `opt_raw_json(k, json_text)`
* `build() -> str`

---

## 3. Adapters

### `http_adapter.nox` (Aether / `nox.http`)
* `json_422(errors: list[FieldError]) -> HttpResponse`: Generates HTTP 422 Unprocessable Entity response with structured JSON error details.
* `json_200(body_json: str) -> HttpResponse`: Generates HTTP 200 OK JSON response.
* `json_201(body_json: str) -> HttpResponse`: Generates HTTP 201 Created JSON response.

### `db_adapter.nox` (Nyx / `nox.db`)
* `row_to_validated_data(row: Row) -> ValidatedData`: Maps `nox.db.Row` into `ValidatedData`.
* `DbAdapter[T](model: ModelSchema[T])`:
  - `parse_row(row: Row) -> T`: Maps a single database row to a typed model.
  - `parse_rows(rows: list[Row]) -> list[T]`: Maps multiple database rows to a typed model list.
