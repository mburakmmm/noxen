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
