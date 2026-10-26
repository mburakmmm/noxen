# Changelog

All notable changes to **Noxen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.2] - 2026-10-26

### Added
- **Database-Managed AUTOINCREMENT Primary Keys**:
  - Replaced manual application-level `self.next_id = self.next_id + 1` in `ProductService` (`examples/realworld_service.nox`) with native SQLite `AUTOINCREMENT` primary key generation.
  - Used `self.conn.last_insert_rowid()` to atomically fetch newly assigned primary keys, eliminating race conditions in concurrent request handling.
- **Adversarial SQL Injection Attack Payloads**:
  - Added Scenario 6 in `examples/realworld_service.nox` executing hostile SQL injection payloads (e.g. `Pwned'); DROP TABLE products; --`).
  - Proves that parametrized `Statement` treat attacks strictly as literal string values: the `products` table remains intact, zero secondary SQL executes, and the malicious string is preserved verbatim.
- **Property-Based Combinatorial Invariant Testing**:
  - Added `tests/fuzz/property_test.nox` testing 192 valid Cartesian product states (combining integer bounds, floating point ratios, string choices, booleans, and nulls/non-null optionals) plus 13 adversarial boundary permutations.
  - Formally proves round-trip preservation, mathematical soundness, error attribution, and `dump_validated` idempotence.
- **Dual-Backend (LLVM & QBE) Benchmark Verification & CI Integration**:
  - Added `examples/realworld_service.nox` to `.github/workflows/ci.yml` runner matrix.
  - Added dual-backend benchmark steps exercising both `--backend llvm` and `--backend qbe`.

## [0.5.1] - 2026-10-26

### Added
- **Parametrized SQL Queries in Service Architectures**:
  - Refactored `ProductService` in `examples/realworld_service.nox` and single record queries in `examples/nyx_crud.nox` to use native `nox.db.Statement` with parametrized `?` binding (`stmt.bind_int`, `stmt.bind_str`).
  - Completely eliminates SQL string concatenation, securing the service layer against SQL injection and guaranteeing safe handling of quotes and apostrophes in text fields (e.g. `"Developer's Precision Desk Mat"`).
  - Added Scenario 5 to `examples/realworld_service.nox` verifying end-to-end insertion, database persistence, and retrieval of records containing special characters and single quotes.
- **Robust Differential Testing Scenario Set Verification**:
  - Upgraded `scripts/verify_json_schema.py` to compare executed scenario names against an explicit `EXPECTED_SCENARIOS` set.
  - Aborts immediately on duplicate scenarios, unexpected scenario names, missing required scenarios, or invalid `noxen_verdict` values.
- **Upgraded Benchmark Methodology**:
  - Integrated 500-iteration warmup phases into `benchmarks/run_benchmarks.nox` to prime instruction caches and runtime branches.
  - Implemented 3-trial execution with median measurement (`median3`) to filter out operating system scheduling jitter.
  - Added checksum accumulators across all benchmark outputs to prevent dead code elimination.

### Changed
- **Serializer Memory Layout Optimization**:
  - Removed the redundant `_written_keys: list[str]` array from `Serializer`.
  - Serializer key collision tracking is now exclusively powered by `_written_map: dict[str, bool]`, eliminating redundant list allocations and reducing memory overhead on every serialized key.

## [0.5.0] - 2026-10-26

### Added
- **Serializer $O(1)$ Hash Key Tracking**:
  - Replaced linear list scanning in `Serializer.has_written_key(k)` with a dedicated hash table `_written_map: dict[str, bool]`.
  - Eliminates $O(N^2)$ cumulative serialization overhead when writing large models with dozens or hundreds of fields.
  - Added stress verification test `test_large_model_o1_key_tracking` in `tests/unit/serializer_strict_test.nox` creating a 100-field serializer and verifying instant duplicate key detection.
- **IEEE 754 Safe Integer Boundary Verification in `dump_validated()`**:
  - Added explicit test coverage in `tests/unit/dump_validated_test.nox` verifying output re-validation around the IEEE 754 safe integer limit ($2^{53} - 1 = 9007199254740991$).
  - Proves that boundary values up to 9007199254740991 pass strict output validation, while values $\ge 9007199254740992$ are rejected with `ValidationError` to protect downstream consumers from precision loss.
- **Hardened JSON Schema Differential Testing**:
  - Hardened `scripts/verify_json_schema.py` to eliminate silent skipping of malformed test lines. Any parsing failure or invalid JSON raises a fatal error immediately.
  - Enforces a minimum threshold of 14 distinct scenarios evaluated against Python's official `Draft202012Validator`, certifying 100% agreement.
- **Dedicated Benchmarks for Fast vs Validated Output Paths**:
  - Added Benchmark 7 (`Validated Model Dump`) to `benchmarks/run_benchmarks.nox`.
  - Measures the performance profile of the ultra-fast direct dump path (1,250,000 ops/sec) alongside the comprehensive validated dump path (555,555 ops/sec).
- **Real-World End-to-End Service Architecture (`examples/realworld_service.nox`)**:
  - Added a comprehensive reference implementation combining Aether (HTTP REST layer) + Nyx (SQLite persistence layer) + Noxen.
  - Demonstrates full CRUD workflow: request body validation via `CreateProductDto`, error reporting with structured HTTP 422 responses (`json_422`), database hydration via `DbAdapter[Product]`, and response generation with `dump_validated()`.

## [0.4.1] - 2026-10-26

### Added
- **Serializer Strict-by-Default Architecture**:
  - `Serializer()` now initializes with strict duplicate key collision protection enabled by default (`strict_keys: bool = True`).
  - Added `.lax() -> Serializer` fluent builder method for explicit opt-out when writing unstructured or raw JSON.
  - Mitigates duplicate JSON key parsing ambiguities and vulnerabilities at the serializer boundary.
- **Output Re-validation Contracts (`dump_validated` & `validate_model`)**:
  - Added `Schema.dump_validated(data: ValidatedData) -> str` and `ModelSchema[T].dump_validated(data: ValidatedData) -> str`.
  - Added `dump_validated(self, obj: T) -> str` and `to_json_validated(self, obj: T) -> str` to `BidirectionalModel[T]` which re-runs full schema validation on the serialized output and raises `ValidationError` if any constraints are violated by mutated model state.
  - Added `validate_model(self, obj: T) -> ValidationResult` to `BidirectionalModel[T]` providing non-throwing validation inspection for HTTP handlers and pipeline middleware.
  - Preserves the ultra-fast 1,250,000 ops/sec `dump(obj)` path while providing strict output verification when required.
- **JSON Schema Differential Testing Engine (Draft 2020-12)**:
  - Upgraded `scripts/verify_json_schema.py` to a complete differential testing engine comparing Noxen's runtime validation verdicts against Python's official `Draft202012Validator`.
  - Exercises a 14-scenario matrix covering nullable/optional presence, numeric bounds, array lengths, regex patterns, enum choices, nested structures, and unknown field rejection under `POLICY_FORBID`.
  - Corrected JSON Schema Draft 2020-12 type emission for nullable fields (`type: ["string", "null"]` / `anyOf: [{ "$ref": ... }, { "type": "null" }]`), achieving 100% agreement across all scenarios.
- **Cross-Platform Windows CI Pipeline**:
  - Added `windows-latest` to the GitHub Actions test matrix in `.github/workflows/ci.yml`.
  - Integrated PowerShell installation script `install.ps1` for automated Windows x86_64 runner validation.
- **Extended Test Suite**:
  - Added `tests/unit/dump_validated_test.nox` covering output re-validation and non-throwing model inspection.
  - Expanded `tests/unit/serializer_strict_test.nox` to verify default strict initialization and `.lax()` opt-out.

## [0.4.0] - 2026-10-26

### Added
- **Bidirectional Typed Model Serialization (Zero Reflection)**:
  - Added `BidirectionalModel[T]` combining a `ModelSchema[T]` parser with an unparser closure `(T) -> ValidatedData`.
  - Enables direct typed model dumping: `model.dump(obj: T) -> str` and `model.to_json(obj: T) -> str` with zero reflection, zero code generation, and 100% static typing.
  - Added `dump_model(self, obj: T, unparser: (T) -> ValidatedData) -> str` and `to_json(self, obj: T, unparser: (T) -> ValidatedData) -> str` directly on `ModelSchema[T]`.
  - Added `set_opt_str`, `set_opt_int`, `set_opt_float`, `set_opt_bool` to `ValidatedData` for streamlined optional/nullable field unparsing.
- **Strict Key Collision Protection Across All Serializer Writers**:
  - `Serializer.strict() -> Serializer` enables strict key validation across all write methods (`str`, `int`, `float`, `bool`, `obj`, `raw`, `list_*`).
  - Raises `ValueError` immediately upon attempting to emit a duplicate JSON property key.
  - Enforced in `tests/unit/serializer_strict_test.nox`.
- **Flat Non-Cyclic `ValidatedData` Architecture & High-Throughput Engine**:
  - Refactored `ValidatedData` into a flat, non-recursive memory layout with hierarchical prefix scoping.
  - Eliminates all recursive class fields, completely bypassing the runtime ARC cycle collector queue.
  - Benchmarks achieve **416,000 to 1,250,000 ops/sec** across flat, nested, 3-level deep hierarchy parsing, and automated model dumps with zero lock contention.
- **Independent JSON Schema Draft 2020-12 Verification**:
  - Resolved root-relative `$defs` aggregation: `to_json_schema()` collects all transitive nested model definitions into a flat root `$defs` dictionary.
  - Added official Draft 2020-12 metaschema verification script (`scripts/verify_json_schema.py`) and integrated it into GitHub Actions CI.
  - Verified valid instance acceptance and strict constraint rejection (numeric bounds, regex patterns, required fields).
- **Public API & Examples Standardization**:
  - All 7 examples in `examples/` standardized to import from the clean top-level `noxen` facade.
  - Extended `benchmarks/run_benchmarks.nox` with 3-level deep hierarchy and bidirectional model serialization suites.

## [0.3.2] - 2026-10-26

### Added
- **Automated Schema-Driven Serialization (Reflection-Free)**:
  - `Schema.dump(data: ValidatedData) -> str` automatically serializes validated data according to declared schema fields, field aliases, nullability, nested models, and lists.
  - `ModelSchema[T].dump(data: ValidatedData) -> str` delegates directly to schema serialization.
  - Automatically incorporates extra properties when `POLICY_ALLOW` is configured.
- **Key Collision Protection in Serializer**:
  - `Serializer` now tracks written keys (`_written_keys`) and exposes `has_written_key(k: str) -> bool`.
  - `include_extras(data)` automatically skips any extra field that collides with an explicitly serialized schema field, guaranteeing duplicate JSON keys are never emitted.
- **Comprehensive Integer Precision & Boundary Test Matrix**:
  - `tests/unit/integer_precision_test.nox` validates exact IEEE 754 safe integer limits ($9007199254740991$ accepted, $9007199254740992$, $9007199254740993$, $-9007199254740992$ rejected).
  - Validates full 64-bit string integer parsing in lax mode ($9223372036854775807$ and $-9223372036854775808$ accepted, $9223372036854775808$ and $-9223372036854775809$ caught as overflow without runtime crash).
- **Extended Database Row Type Fidelity Tests**:
  - Expanded `tests/integration/db_adapter_test.nox` to verify strict SQL column typing across `REAL` (float), `INTEGER` (int), `INTEGER` (bool 0/1), and `TEXT` (strings), including error enforcement for out-of-bounds numbers and invalid booleans.

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
