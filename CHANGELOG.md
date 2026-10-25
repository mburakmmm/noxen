# Changelog

All notable changes to **Noxen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
