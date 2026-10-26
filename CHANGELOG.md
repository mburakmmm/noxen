# Changelog

All notable changes to **Noxen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.3] - 2026-10-26

### Added
- **Zero-Boilerplate Automatic Model Creation (`Model` & `auto_model`)**:
  - Implemented `Model` class and `auto_model(class_name: str) -> Model` allowing instant model instantiation directly from class reflection metadata without requiring manual factory (`make_model`) or unparser closures.
  - Supports fluent property accessors (`get_str`, `get_int`, `get_float`, `get_bool`, `get_opt_*`, `get_list_*`, `get_object`) and mutators (`set_str`, `set_int`, etc.).
  - Added direct validation and serialization helpers: `model.parse_json()`, `model.to_json()`, `model.to_json_validated()`, and `model.to_json_schema()`.
  - Added dedicated unit test suite `tests/unit/auto_model_test.nox`.
- **Simplified IEEE 754 Finiteness Without Division-by-Zero (P0)**:
  - Simplified `is_finite_float(v: float) -> bool` to `(v == v) and ((v - v) == 0.0)`, completely eliminating explicit `1.0 / 0.0` division-by-zero expressions while preserving 100% mathematical IEEE 754 rigor for NaN, +inf, and -inf.
- **Dynamic Real-Result Semantic Parity Markers (P1)**:
  - Upgraded structured `NOXEN_RESULT_JSON` markers across all 12 test and example targets to dynamically include verified runtime outcomes, exact case counts, and numeric values (e.g. `roundtrip_val`, `permutations`, `sections_passed`, `symbols_verified`).
- **Comprehensive Public API Contract & Regression Suite (P1)**:
  - Added `tests/unit/api_compatibility_test.nox` verifying the stability of all public constants, exports, fluent methods, adapters, and presence modes.
- **Randomized Property-Based Fuzzing with 1,000 Permutations (P1)**:
  - Added an adversarial linear congruential pseudo-random property fuzzer to `tests/fuzz/property_test.nox` testing 1,000 permutations of random integer ranges, float bounds, corrupt keys, and unicode strings.
- **Automated Mutation Testing Suite (P2)**:
  - Added `scripts/run_mutation_tests.py` verifying that core validation and serialization logic achieves a 100% mutation kill score (0 surviving mutants).
- **Performance Regression Gate (P2)**:
  - Added `scripts/check_performance_regression.py` enforcing minimum throughput floors (ops/sec) to prevent latency regressions across commits.
  - Added mutation testing and performance regression steps to CI workflow (`.github/workflows/ci.yml`).

## [0.7.2] - 2026-10-26

### Added
- **Serializer State Integrity on Validation Failures**:
  - Reordered validation logic in `Serializer.float`, `Serializer.opt_float`, `Serializer.list_float`, `Serializer.raw_json`, and `Serializer.opt_raw_json` so all validations occur *strictly before* `_record_key(k)` is invoked.
  - If a value fails validation (e.g. non-finite float or malformed raw JSON), the key is never recorded into `_written_map`. Subsequent valid writes with the same key succeed without spurious duplicate key errors under strict mode.
  - Added dedicated unit tests in `tests/unit/serializer_strict_test.nox` verifying state non-mutation across primitive, optional, list, and raw JSON serialization paths.
- **Pure Mathematical IEEE 754 Finiteness Check (`is_finite_float`)**:
  - Replaced string formatting dependency (`str(v) == "nan"`) with pure mathematical IEEE 754 axioms: `v != v` (detecting NaN) and `(v - v) != 0.0` (detecting +-Infinity).
  - Exported `is_finite_float(v: float) -> bool` from `serialization.nox` and top-level `noxen.nox`.
- **Negative Zero (`-0.0`) Serialization & Round-Trip Preservation**:
  - Expanded `tests/unit/float_edge_cases_test.nox` to verify that `-0.0` serialized to JSON formats as `"-0.0"` and re-parses with preserved IEEE 754 negative sign (`1.0 / val == -inf`).
- **100% Structured Semantic Parity Markers Across All 10 Targets**:
  - Added `NOXEN_RESULT_JSON` structured markers to `tests/fuzz/property_test.nox`, `examples/realworld_service.nox`, `examples/nested_model.nox`, `examples/strict_validation.nox`, `examples/custom_validator.nox`, and `examples/json_roundtrip.nox`.
  - Upgraded `scripts/verify_backend_parity.py` to require `expected_markers: 1` on all 10 targets, eliminating skipped semantic targets and ensuring 100% parity verification between LLVM and QBE.
- **Recursive Models & JSON Schema `$ref` Roadmap Documentation**:
  - Documented future post-1.0 plans for self-referential models via JSON Schema Draft 2020-12 `$defs` and `$ref` lazy pointers in `docs/architecture.md` and `docs/roadmap.md`.

## [0.7.1] - 2026-10-26

### Added
- **Non-Finite Float Serialization Rejection**:
  - `Serializer.float`, `Serializer.opt_float`, `Serializer.list_float`, and `Schema.dump` now strictly check for non-finite values (`NaN`, `Infinity`, `-Infinity`) and raise `ValueError`, preventing generation of malformed JSON.
  - Added test cases to `tests/unit/float_edge_cases_test.nox` verifying rejection across all serialization paths.
- **Exact IEEE 754 Negative Zero (`-0.0`) Sign Preservation**:
  - Added mathematical IEEE 754 sign verification (`1.0 / -0.0 == -inf`, `1.0 / 0.0 == inf`) to prove exact sign preservation without relying solely on approximate equality.
- **Recursive Model Cycle Detection in `auto_schema`**:
  - Implemented derivation call stack tracking to detect self-referential or cyclic models (e.g. `Category` containing `Category | None`), raising an immediate descriptive `ValueError` and eliminating infinite recursion.
- **Strict Unsupported Parameter Type Rejection**:
  - `auto_schema` now validates every parameter type against supported Nox types; unrecognized or unmappable types raise `ValueError` immediately, preventing silent data omission.
- **Dual-Mode Backend Parity Verification (`scripts/verify_backend_parity.py`)**:
  - Added CLI flag `--mode`:
    - `--mode semantic`: Validates structured `NOXEN_RESULT_JSON` markers and semantic JSON equivalence (with zero silent exception suppression).
    - `--mode strict`: Enforces byte-for-byte stdout and exit code equivalence.
    - `--mode all`: (Default) Executes both semantic structured validation and strict byte-for-byte verification.
  - Added `NOXEN_RESULT_JSON` markers to `nested_array_test.nox`, `auto_model.nox`, `auto_schema_test.nox`, and `float_edge_cases_test.nox`.
- **Architectural Clarity & Model Mapping Documentation**:
  - Clarified the distinction between automatic schema derivation and explicit type-safe model mapping in `README.md`, `docs/architecture.md`, and `docs/api.md`, documenting the language invariants of ahead-of-time compiled Nox.

## [0.7.0] - 2026-10-26

### Added
- **Zero-Boilerplate Automatic Schema Derivation (`auto_schema`)**:
  - Implemented `auto_schema(class_name: str) -> Schema` and `schema_from_class(class_name: str) -> Schema` leveraging the standard library `nox.reflect` module.
  - Automatically inspects class signatures and constructor parameters without any manual field declaration overhead.
  - Recursively resolves and binds:
    - Primitive types (`str`, `int`, `float`, `bool`)
    - Optional & nullable primitives and models (`T | None`) as `.optional().nullable()`
    - Primitive arrays (`list[str]`, `list[int]`, `list[float]`, `list[bool]`)
    - Nested models and sub-schemas (`field_object`)
    - Arrays of nested models (`field_list_schema`)
  - Added `Schema.derive_from_class(class_name: str) -> Schema` for fluent class-to-schema population.
  - Added `Schema.require_field(name: str) -> Field` to eliminate optional-narrowing boilerplate when attaching fluent constraints (`min_i`, `max_i`, `email`, etc.).
  - Added `Field.is_nullable() -> bool`, `Field.is_optional() -> bool`, and `Field.is_required() -> bool` inspection helpers.
  - Added comprehensive unit test `tests/unit/auto_schema_test.nox` and dedicated runnable example `examples/auto_model.nox`.
- **Multi-Level Deep Equality Assertions for Nested Array Round-Trips**:
  - Upgraded `tests/integration/nested_array_test.nox` with `assert_company_deep_eq`, asserting 100% of fields across all array elements and sub-objects (`Company -> employees[] -> addresses[]`) byte-for-byte during round-trip serialization.
- **Float Special Values Policy & Boundary Verification**:
  - Implemented RFC 8259-compliant rejection of non-finite floats (`NaN`, `Infinity`, `-Infinity`) during JSON parsing and lax string coercion.
  - Added dedicated test suite `tests/unit/float_edge_cases_test.nox` verifying negative zero (`-0.0`), subnormals (`1e-15`), large finite floats (`1.7976931348623157e+308`), numeric range bounds, and adaptive relative float equality (`is_float_approx_eq`).
- **Semantic & Structured Backend Parity Verification**:
  - Upgraded `scripts/verify_backend_parity.py` beyond raw stdout comparison to extract, parse, and semantically compare structured JSON verdicts and state outputs between LLVM and QBE across 10 core targets.
- **Deterministic CI Pinning**:
  - Pinned installer scripts in `.github/workflows/ci.yml` to release tag `v2.0.27` (`https://raw.githubusercontent.com/mburakmmm/nox-lang/v2.0.27/install.sh` and `install.ps1`) for reproducible builds.

## [0.6.0] - 2026-10-26

### Added
- **Multi-Level Nested Array & Object Hierarchies**:
  - Added `tests/integration/nested_array_test.nox` exercising multi-level object-in-array compositions (`Company -> employees[] -> addresses[]`).
  - Proves deep error path attribution (e.g. `employees[1].addresses[0].city`), non-object element rejection (`employees[0].addresses[0]`), and round-trip serialization (`dump` & `dump_validated`) preserving all array lengths and sub-object properties.
  - Added Invariant Property 6 to `tests/fuzz/property_test.nox` verifying `Cluster -> nodes[] -> locations[]` round-trip.
- **Adaptive Relative Epsilon Float Precision**:
  - Replaced fixed absolute epsilon (`0.0001`) with adaptive relative comparison `is_float_approx_eq` with 1 part per million relative tolerance and $10^{-9}$ absolute floor.
  - Guarantees high-fidelity float serialization without drift across both tiny ($10^{-7}$) and large ($1,234,567.89$) floats, while strictly rejecting coarse variations (e.g. `0.123456` vs `0.1235`).
- **Expanded Unicode, Control Character & Buffer Edge Cases**:
  - Added combining Unicode sequences (e.g. `e\u0301`, `a\u0308`), control characters (`\b`, `\f`), and 5,000-character multi-byte UTF-8 payloads to `tests/fuzz/property_test.nox`.
- **Automated Dual-Backend (LLVM & QBE) Parity Verification**:
  - Created `scripts/verify_backend_parity.py` executing 7 core targets (`property_test.nox`, `nested_array_test.nox`, `realworld_service.nox`, `nested_model.nox`, `strict_validation.nox`, `custom_validator.nox`, `json_roundtrip.nox`) under both `--backend llvm` and `--backend qbe`.
  - Asserts 100% byte-for-byte stdout and exit code parity between backends.
  - Integrated parity verification into `.github/workflows/ci.yml`.
- **Documentation & Precision Claims**:
  - Clarified JSON Schema specification agreement in `README.md` to precisely reflect currently implemented differential scenarios.
  - Added compiler version (`noxc 2.0.27`), warmup iterations, and dual-backend benchmark performance metrics.

## [0.5.3] - 2026-10-26

### Added
- **Full-Field Combinatorial Round-Trip Verification**:
  - Upgraded `tests/fuzz/property_test.nox` to assert 100% of model fields across all 192 valid Cartesian combinations:
    - `id`: integer equality (`assert_eq_int`)
    - `tag`: choice string equality (`assert_eq_str`)
    - `active`: boolean equality
    - `ratio`: floating point precision preservation within $\epsilon < 10^{-4}$
    - `notes`: strict null-state vs string-content round-trip verification across both `None` and populated string states.
- **Expanded Invariant & Adversarial Fuzzing Coverage**:
  - **Unicode String Invariant**: Tested 9 diverse character sets and escape patterns including Turkish characters (`çğıöşü ÇĞİÖŞÜ`), European accented letters, Asian ideograms (Japanese/Chinese/Korean), Cyrillic, emoji sequences, quotes, backslashes, newlines, tabs, and empty/whitespace strings. Validates zero byte degradation and exact string round-trip equivalence.
  - **Float Precision & Boundary Invariant**: Verified precision retention across float boundaries (`0.0`, `1.0`, `0.00001`, `0.99999`, `0.123456`, `12345.6789`, `-42.5`).
  - **Nested Model Invariant**: Multi-level hierarchy round-trip (`MachineRecord` containing nested `HardwareSpecs`) verifying that outer identifiers and inner nested fields (including nullable/optional GPU models) preserve schema validity and value fidelity.
  - **Adversarial Permutations**: Expanded to 17 adversarial checks covering boundary out-of-range bounds, invalid choice sets, string-for-int type mismatches, non-strict boolean numbers under strict mode, missing required fields, and unexpected extra fields under `POLICY_FORBID`.
- **Framework-Independent Zero-Dependency Adapter Contract**:
  - Formalized AGENTS.md §0 & §2 zero-framework dependency invariants in `docs/architecture.md` and `docs/compatibility.md`: Noxen core and adapters interact exclusively via standard `nox.http` (`HttpRequest`, `HttpResponse`) and `nox.db` (`Row`, `Statement`).
- **Documented Dual-Backend Performance Baselines**:
  - Documented benchmark baselines for LLVM (454k - 1.25M ops/sec) and QBE (384k - 1.25M ops/sec) in `docs/compatibility.md`.

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
