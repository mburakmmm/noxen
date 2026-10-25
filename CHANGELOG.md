# Changelog

All notable changes to **Noxen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-10-26

### Fixed
- **Database Row Validation Enforced**:
  - `DbAdapter[T].parse_row` and `DbAdapter[T].parse_rows` now rigorously validate all database columns against the model's schema before hydrating the object.
  - Invalid database rows raise `ValidationError` with structured error items.
  - Non-throwing validation added via `DbAdapter[T].parse_row_result(row) -> Result[T]` and `validate_row(row) -> ValidationResult`.
- **Integer Precision & 64-Bit Boundaries**:
  - Added exact 64-bit integer bounds (`min_i`, `max_i`, `ge_i`, `le_i`) on `Field` preventing float conversion precision loss.
  - Formatted integer bounds in JSON Schema generator directly as integers without float casting.
- **Documentation & Facade Consistency**:
  - Corrected `ModelSchema[T].validate` documentation in `docs/api.md`.
  - Added `Serializer.include_extras(data)` enabling automatic passthrough of extra attributes captured under `POLICY_ALLOW`.
  - Documented exact supported ISO 8601 subset and Integer Precision Policy ($[-2^{53}+1, 2^{53}-1]$ for JSON numbers, 64-bit string integers for large IDs).

## [0.3.0] - 2026-10-26

### Added
- **ISO 8601 Date & Time Constraints**:
  - `.date()` validates calendar dates (`YYYY-MM-DD`, with leap year verification).
  - `.time()` validates 24-hour time (`HH:MM:SS` with optional timezone/fractional seconds).
  - `.datetime()` validates combined ISO 8601 timestamps (`YYYY-MM-DDTHH:MM:SS[Z]`).
  - Added stable error codes `CODE_INVALID_DATE`, `CODE_INVALID_TIME`, `CODE_INVALID_DATETIME`.
- **Sensitive Data Redaction**:
  - `.secret()` marks sensitive credentials (passwords, tokens, keys). Error outputs automatically replace raw actual values with `[REDACTED]`.
- **Unknown Fields Preservation Policy (`POLICY_ALLOW`)**:
  - `POLICY_ALLOW` permits extra JSON properties and stores them safely in `ValidatedData` accessible via `get_extra_keys()` and `get_extra(key)`.
- **JSON Schema `$defs` / `$ref` Support**:
  - Nested schemas are extracted into a top-level `$defs` dictionary and referenced with `{"$ref": "#/$defs/ModelName"}` according to JSON Schema Draft 2020-12.
- **Fuzz & Adversarial Test Suite**:
  - `tests/fuzz/fuzz_test.nox` tests malformed JSON, boundary attacks, deep nesting recursion limit enforcement, error caps, and multi-byte Unicode.
- **Multi-OS CI Matrix**:
  - Updated `.github/workflows/ci.yml` with a cross-platform test matrix running on both Linux (`ubuntu-latest`) and macOS (`macos-latest`).
- **Complete Modular Documentation**:
  - Added `docs/api.md`, `docs/security.md`, `docs/roadmap.md`, `docs/migration.md`, and `docs/serialization.md`.

## [0.2.0] - 2026-10-26

### Added
- **Field Aliasing**:
  - `alias(json_key)` allows mapping incoming JSON keys (e.g. `camelCase` or reserved keywords) to internal model field names.
- **Allowed Value Sets / Enums**:
  - `in_choices(list[str])` for string literals and enumerations.
  - `in_choices_int(list[int])` for numeric enumerations.
- **Array Size Constraints**:
  - `min_items(n)` and `max_items(n)` for list fields.
- **Extended Numeric Constraints**:
  - Added `ge(v)` (greater or equal) and `le(v)` (less or equal) alongside `gt(v)` and `lt(v)` exclusive bounds.
- **Coercion Modes**:
  - `COERCION_STRICT` (strict default, no implicit type casting).
  - `COERCION_LAX` for opt-in safe conversions of stringified numbers and booleans.
- **Resource & Security Limits**:
  - Configurable `max_depth` (default: 32) with automatic inheritance across nested schemas to prevent stack exhaustion on adversarial inputs.
  - Configurable `max_errors` (default: 50) to cap error accumulation and prevent unbounded allocations.
- **Aether Framework Integration Adapter**:
  - `http_adapter.nox` with `json_422`, `json_200`, and `json_201` helpers producing standard `nox.http.HttpResponse` objects with RFC 7807/machine-readable validation error bodies.
- **Nyx Database Integration Adapter**:
  - `db_adapter.nox` with generic `DbAdapter[T]` and `row_to_validated_data` converting `nox.db.Row` (SQLite, PostgreSQL, MySQL) into typed models.
- **Comprehensive Examples**:
  - `examples/aether_server.nox`: End-to-end HTTP request DTO validation, 422 error generation, and 201 JSON response creation.
  - `examples/nyx_crud.nox`: In-memory SQLite CRUD workflow reading rows and hydrating typed `Book` models.
- **High-Performance Benchmark Suite**:
  - `benchmarks/run_benchmarks.nox`: Benchmarks demonstrating 600,000 to 1,000,000+ operations per second on native Nox.
- **Documentation**:
  - `docs/integrations.md`: Complete guide for integrating Noxen with Aether HTTP web applications and Nyx database access.

## [0.1.0] - 2026-10-26

### Added
- **Phase 0 & Core MVP**:
  - `errors.nox`: Machine-readable `FieldError` with stable error codes and `ValidationError(Exception)`.
  - `core.nox`: `ValidatedData` structured container, `ValidationResult`, and generic `Result[T]` with `unwrap()` and `unwrap_or()`.
  - `schema.nox`: Declarative `Schema` and `Field` definitions, supporting 4 presence modes (`REQUIRED`, `REQUIRED_NULLABLE`, `OPTIONAL`, `OPTIONAL_NULLABLE`).
  - Unknown fields policy: `POLICY_FORBID` (strict default) and `POLICY_IGNORE`.
  - Primitive constraints: `min`, `max`, `min_length`, `max_length`, `regex`.
  - Format validators: email, absolute HTTP/HTTPS URL via `nox.url`, standard UUID format.
  - Nested object models (`field_object`) and array validation (`field_list`, `field_list_schema`).
  - Custom validator callback hooks (`add_validator`) for cross-field validations.
  - JSON Schema generation adhering to JSON Schema Draft 2020-12.
  - `models.nox`: `ModelSchema[T]` generic parser binding JSON to typed Nox classes.
  - `serialization.nox`: `Serializer` fluent builder for serializing models and fields into valid JSON.
  - Namespaced module re-exports in `noxen/`.
  - Automated test suite covering 9 unit and integration test modules.
  - Compiling examples for basic models, nested models, strict validation, JSON round-trips, and custom validators.
  - Comprehensive documentation in `docs/` (`compatibility.md`, `architecture.md`, `validation.md`).
  - GitHub Actions CI workflow in `.github/workflows/ci.yml`.
