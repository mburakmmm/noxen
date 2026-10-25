# Changelog

All notable changes to **Noxen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
