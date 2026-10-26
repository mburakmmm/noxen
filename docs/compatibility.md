# Compatibility Matrix & Environment Audit — Noxen

> Status: Verified against `noxc 2.0.27` on Darwin arm64.

## 1. Toolchain & Runtime Baseline

| Attribute | Verified Value | Evidence |
|---|---|---|
| Compiler version | `noxc 2.0.27` | `noxc --version` output |
| Compiler path | `/Users/melihburakmemis/.nox-lang/bin/noxc` | `which noxc` |
| Default backend | LLVM (`--backend llvm`) | `noxc --help` / `docs/tools/noxc.md` |
| Fallback backend | QBE (`--backend qbe`) | Freestanding / line debug (`-g`) |
| Host platform | macOS Darwin arm64 (`macos-arm64`) | `uname -s -m` |
| Build command | `noxc build <file.nox>` | Verified with `noxc build` |
| Run command | `noxc run <file.nox>` | Verified with `noxc run` |
| Test command | `noxc test [path]` | Verified with `noxc test` |
| Check command | `noxc check <file.nox>` | Verified with `noxc check` |
| Formatter | `noxc fmt <file.nox>` | Available in toolchain |
| Project init | `noxc init <name>` | Available in toolchain |
| Publish | `noxc publish <repo>` | Central index metadata submit |

## 2. Standard Library Analysis

### `nox.json`
- **Parser**: Native parser backed by Zig's `std.json` via runtime shim.
- **Tree**: `JsonValue` prelude type with scalar kind tests (`is_null`, `is_bool`, `is_number`, `is_string`, `is_array`, `is_object`).
- **Accessors**:
  - Scalars: `as_bool`, `as_number` (returns `float`), `as_string`.
  - Arrays: `array_len`, `array_get`.
  - Objects: `object_len`, `object_key`, `object_value` (**preserves document order**).
- **Serializers**:
  - `dump(v: JsonValue) -> str`
  - `dump_pretty(v: JsonValue, indent: int) -> str`
  - `dump_string(s: str) -> str` (proper C0/escape handling)
  - `dump_number(n: float) -> str` (whole numbers formatted without `.0`)
  - `JsonWriter`: Append-only builder (`begin_object`, `end_object`, `begin_array`, `end_array`, `write_key`, `write_string`, `write_int`, `write_float`, `write_bool`, `write_null`, `write_value`, `build`).
- **Limitations**:
  - All JSON numbers in `JsonValue` are stored as `float` (IEEE 754 double).
  - Objects do not have hash indexes; key lookup requires linear iteration over keys (optimal for typical JSON payload sizes).

### `nox.validate`
- **Existing Capability**:
  - Declarative schema validation returning `list[str]` human-readable English errors.
  - Supports field rules (`require`, `optional`), nested objects (`require_object_schema`), arrays (`require_array_of_kind`, `require_array_of_schema`).
  - Primitive constraints: `min`, `max`, `min_length`, `max_length`, `pattern`, `format` (`"email"`, `"uuid"`).
- **Identified Limitations (Opportunities for Noxen)**:
  - Returns raw untyped `list[str]` rather than structured, machine-readable error objects with stable error codes, structured paths, and severity.
  - Does NOT construct typed objects (classes); consumers must manually extract fields from `JsonValue`.
  - Does NOT support unknown field policies (unexpected fields are silently accepted/ignored).
  - Does NOT distinguish `null` from missing on optional fields (no true nullability policy).
  - Does NOT support field default values.
  - Does NOT generate JSON Schema standard specifications.
  - Does NOT support URL format validation or custom validator callbacks.
  - Does NOT support typed object -> JSON serialization.

### `nox.url`
- High performance RFC-compliant URL parser:
  - `parse(s: str) -> URL` splits scheme, userinfo, host, port, path, query, fragment.
  - Raises `UrlError` on malformed URLs.
  - Used by Noxen for robust URL format validation.

### `nox.reflect`
- Exposes constructor reflection metadata:
  - `class_count()`, `class_name(i)`, `class_index(name)`.
  - `class_init_param_count(i)`, `class_init_param_name(i, k)`, `class_init_param_type(i, k)`.
- Verified capability: Can inspect model field names and types (e.g., `str`, `int`, `str | None`).
- Verified limitation: Cannot dynamically instantiate arbitrary classes without explicit code.

### `nox.test`
- Assertions: `assert_eq_int`, `assert_eq_str`, `assert_eq_float`, `assert_true`.
- Test harness: `TestSuite` with `check_*` methods and JUnit XML reporter.

## 3. Package & Module Resolution Rules

- In Nox, package aliases are configured in `nox.json` (`requires: [...]`).
- When a consumer imports `import noxen.core`:
  - `segments[0]` (`"noxen"`) is matched against the package alias.
  - `segments[1..]` (`"core"`) resolves to `<package_root>/core.nox`.
- Within the Noxen repository itself:
  - A dual-layout structure is adopted:
    - Root modules: `core.nox`, `errors.nox`, `fields.nox`, `schema.nox`, `validators.nox`, `json.nox`.
    - Namespaced directory `noxen/`: Contains re-export shims (`noxen/core.nox`, etc.) so that both `import core` and `import noxen.core` resolve identically regardless of execution context (internal test run vs external dependency consumption).

## 4. Architectural Decisions & Fallbacks

1. **No Fake Reflection / No Dynamic `setattr`**:
   Nox is strictly statically typed and ahead-of-time compiled without dynamic evaluation. Noxen uses a typed factory/companion mapping pattern `(ValidatedData) -> T` and `(T, JsonWriter) -> None` which preserves full type safety, static checks, and zero-cost dispatch.
2. **Deterministic Validation Pipeline**:
   Field validation runs strictly in schema definition order. Errors are collected deterministically into structured `FieldError` objects.
3. **Strict by Default**:
   Unknown fields are rejected by default (`Policy.FORBID`), adhering to AGENTS.md §5 and §8.
4. **Distinction between Missing and Null**:
   A field can be `REQUIRED_NON_NULL`, `REQUIRED_NULLABLE`, `OPTIONAL_NON_NULL` (can be omitted, but if present cannot be null), or `OPTIONAL_NULLABLE` (can be omitted or null).

## 5. Ecosystem Adapter & Generic Class Findings (v0.2.0)

### `nox.http` (Aether Interop)
- `nox.http.HttpResponse(status: int, body: str, headers: dict[str, str])`
- `nox.http.HttpRequest(method: str, path: str, body: str, headers: dict[str, str], remote_addr: str)`
- Noxen's `http_adapter.nox` provides `json_422(errors: list[FieldError]) -> HttpResponse` and `json_200`/`json_201` producing RFC 7807/machine-readable validation response bodies for Aether web handlers.

### `nox.db` and `nox.sqlite` (Nyx Interop)
- `nox.db.Row` stores column values as strings and provides `.column_count()`, `.column_name(i)`, `.is_null(i)`, `.get_str(i)`, `.get_int(i)`, `.get_float(i)`.
- Shared row type is unified across SQLite, PostgreSQL, and MySQL.
- Noxen's `db_adapter.nox` provides `row_to_validated_data(row: Row) -> ValidatedData` and `DbAdapter[T](model)` providing `.parse_row(row: Row) -> T` and `.parse_rows(rows: list[Row]) -> list[T]`.

### Generic Method vs Free Function Monomorphisation
- **Finding**: In Nox 2.0.27, generic type brackets `[T]` are valid on classes (`class DbAdapter[T]: ...`), but calling generic free functions `def fn[T](...) -> ...` fails with `unknown generic constructor: fn`.
- **Decision**: All generic operations are modeled as methods on monomorphised classes (`ModelSchema[T]`, `Result[T]`, `DbAdapter[T]`, `BidirectionalModel[T]`). Non-generic helpers remain free functions.

## 6. Compiler Invariants & Architecture Discoveries (v0.4.0)

### Generic Type Re-Export Limitation
- **Finding**: In `noxc 2.0.27`, re-exporting generic classes across package aliases (`from core import Result` re-exported in `noxen.nox` as `from noxen import Result`) causes `unknown generic type: Result` at consumer call sites.
- **Decision**: Consumers import generic classes (`ModelSchema[T]`, `Result[T]`, `BidirectionalModel[T]`, `DbAdapter[T]`) directly from their defining module (`models`, `core`, `db_adapter`), while non-generic types (`Schema`, `Field`, `Serializer`, `ValidatedData`, `json_422`, etc.) are imported from the clean top-level `noxen` facade.

### Method Self-Recursion Codegen Restriction
- **Finding**: Direct self-recursion on class methods (`def collect(self): self.collect()`) triggers compiler codegen failure: `codegen: this program contains a construct that is not supported`.
- **Decision**: Hierarchical traversals (such as JSON Schema nested `$defs` aggregation) are implemented using an iterative worklist queue (`while qi < len(queue): ...`) rather than recursive method calls.

### Flat Non-Cyclic `ValidatedData` Layout
- **Finding**: Classes with fields containing instances of their own type (e.g. `_objs: dict[str, ValidatedData]`) are analyzed by the compiler's `computeCyclicClasses` graph and registered as potential cycle roots in the runtime's cycle collector. When dropped inside synchronous GC passes, re-entrant lock acquisition can stall the spinlock.
- **Decision**: `ValidatedData` uses a flat, prefix-scoped dictionary architecture (`_strs`, `_ints`, etc.) with zero class-typed fields. This eliminates all recursive class tracking, completely bypassing cycle collector queues while boosting parsing throughput to **416,000–1,250,000 ops/sec**.

### JSON Schema Draft 2020-12 `$defs` Specification
- **Finding**: In JSON Schema Draft 2020-12, all `$ref: "#/$defs/..."` pointers must resolve from the root document. Nested sub-schemas must not encapsulate local `$defs` or `$schema` keywords.
- **Decision**: `Schema.to_json_schema()` collects all child and grandchild schema definitions into a unified root-level `$defs` dictionary, verified against the official JSON Schema Draft 2020-12 metaschema via independent validation.

## 7. Fuzzing, Invariants & Adapter Architecture (v0.5.3)

### Optional Member Attribute Type Narrowing
- **Finding**: In `noxc 2.0.27`, compiler type-narrowing on `if x is not None:` applies strictly to local variable symbols. Narrowing an optional member attribute on an object instance (e.g. `if obj.optional_field is not None:`) does not propagate narrowed non-optional types to member accesses in the guarded body.
- **Decision**: Explicitly unpack member fields into local variables before type-narrowing assertions:
  ```nox
  val: str | None = obj.optional_field
  if val is not None:
      nox.test.assert_eq_str(val, expected, "verified")
  ```

### Zero-Framework Dependency Adapter Contract
- **Finding**: High-level web and ORM frameworks (Aether, Nyx) frequently evolve route handler and repository interfaces. Tying the data modeling core to framework packages creates circular dependencies and dependency lock-in.
- **Decision**: Noxen core maintains strictly **zero third-party dependencies**. Integrations are provided via lightweight protocol adapters (`http_adapter.nox`, `db_adapter.nox`) built entirely on the Nox standard library (`nox.http` and `nox.db`).

### Dual-Backend Benchmark Performance Baselines
- **LLVM Backend (`--backend llvm`)**:
  - Flat Model Parsing: 625,000 ops/sec (8 ms / 5,000 ops)
  - Nested Model Parsing: 555,555 ops/sec (9 ms / 5,000 ops)
  - Fast Model Serialization: 1,250,000 ops/sec (4 ms / 5,000 ops)
  - Validated Model Dump: 625,000 ops/sec (8 ms / 5,000 ops)
- **QBE Backend (`--backend qbe`)**:
  - Flat Model Parsing: 555,555 ops/sec (9 ms / 5,000 ops)
  - Nested Model Parsing: 500,000 ops/sec (10 ms / 5,000 ops)
  - Fast Model Serialization: 1,250,000 ops/sec (4 ms / 5,000 ops)
  - Validated Model Dump: 555,555 ops/sec (9 ms / 5,000 ops)

## 8. Nested Arrays, Parity & Relative Float Epsilon (v0.6.0)

### Multi-Level Nested Array Hierarchies
- **Finding**: Nested arrays of structured objects (`Company -> employees[] -> addresses[]`) require recursive prefix management (`employees[0].addresses[1].city`) to avoid object dictionary collisions and preserve proper validation path attribution.
- **Decision**: `ValidatedData` uses dot-and-bracket prefixing for array items (`item_pfx: str = pk + "[" + str(idx) + "]."`). `Schema.dump()` automatically traverses nested array schemas with `item_kind == "object"`, and `tests/integration/nested_array_test.nox` verifies end-to-end parsing, error paths, and round-trip serialization.

### Adaptive Relative Float Epsilon
- **Finding**: Fixed absolute epsilon thresholds (`0.0001`) allow coarse drift on numbers like `0.123456` returning as `0.1235`. Conversely, fixed thresholds can fail on very small floats (`1e-7`) or very large numbers.
- **Decision**: Adopted an adaptive comparison function `is_float_approx_eq` with 1 PPM relative tolerance ($10^{-6}$) and a $10^{-9}$ absolute tolerance floor near zero. Formally verified to reject `0.123456 vs 0.1235` while confirming exact IEEE 754 precision retention across small and large values.

### Automated LLVM & QBE Backend Parity
- **Finding**: Differences in intermediate representations or calling conventions between LLVM and QBE backends can introduce silent behavioral divergence on complex string manipulation or monomorphised generic classes.
- **Decision**: Implemented `scripts/verify_backend_parity.py` running 7 core test and service suites across both backends. Verifies 100% byte-for-byte stdout, stderr, and exit code equivalence.


