# Noxen Validation Semantics & Decision Table

## 1. Presence & Nullability Matrix

Noxen strictly separates key existence (**missing**) from explicit `null` (**present with null**).

| Rule Mode | Key Missing | Key Present with `null` | Key Present with Value | Default Applied? |
|---|---|---|---|---|
| `REQUIRED` (Default) | Error: `missing_field` | Error: `unexpected_null` | Valid (if type matches) | No |
| `REQUIRED_NULLABLE` | Error: `missing_field` | Valid (yields `None`) | Valid (if type matches) | No |
| `OPTIONAL` | Valid (yields `None` or Default) | Error: `unexpected_null` | Valid (if type matches) | Yes (on missing only) |
| `OPTIONAL_NULLABLE` | Valid (yields `None` or Default) | Valid (yields `None`) | Valid (if type matches) | Yes (on missing only) |

### Key Invariant
Defaults are **only applied on missing keys**, never when a key is explicitly provided as `null` or with an invalid value.

---

## 2. Type Checking Matrix

Strict mode (`COERCION_STRICT`) is enabled by default. Coercion is forbidden unless `COERCION_LAX` is explicitly configured.

| Target Type | Valid JSON Input | Invalid Inputs (produce `type_mismatch`) |
|---|---|---|
| `string` | JSON string `"text"` | Numbers (`123`), Booleans (`true`), Arrays, Objects, Null |
| `int` | JSON integer `42`, `-7` | Fractional numbers (`42.5`), Strings (`"42"` in strict mode), Booleans, Null |
| `float` | JSON number `42.5`, `42` | Strings (`"42.5"` in strict mode), Booleans, Null |
| `bool` | JSON boolean `true`, `false` | Numbers (`1`, `0`), Strings (`"true"`, `"false"` in strict mode), Null |
| `list[T]` | JSON array `[...]` | Non-array values |
| `object` | JSON object `{...}` | Non-object values |

---

## 3. Numeric Constraints & Precision Policies

| Constraint | Applicable Types | Condition | Error Code |
|---|---|---|---|
| `min(v)` / `ge(v)` | `int`, `float` | Value must be $\ge v$ | `out_of_range` |
| `max(v)` / `le(v)` | `int`, `float` | Value must be $\le v$ | `out_of_range` |
| `gt(v)` | `int`, `float` | Value must be $> v$ | `out_of_range` |
| `lt(v)` | `int`, `float` | Value must be $< v$ | `out_of_range` |
| `min_i(v)` / `ge_i(v)` | `int` | Pure 64-bit integer $\ge v$ without float precision loss | `out_of_range` |
| `max_i(v)` / `le_i(v)` | `int` | Pure 64-bit integer $\le v$ without float precision loss | `out_of_range` |
| `in_choices_int(opts)` | `int` | Value must belong to allowed integer set | `choice_mismatch` |

### Integer Precision Policy
1. **JSON Number Limits**: Raw JSON numbers in `nox.json` are parsed as IEEE 754 float64. Noxen bounds safe numeric integers to $[-2^{53} + 1, 2^{53} - 1]$ ($[-9007199254740991, 9007199254740991]$). Any JSON number outside this range is rejected to prevent silent precision loss.
2. **Full 64-Bit Integers**: For 64-bit IDs or timestamps up to $2^{63}-1$, values transmitted as strings are coerced to 64-bit integers under `COERCION_LAX`.
3. **Exact Bounds**: Integer constraints (`min_i`, `max_i`) store and evaluate 64-bit integers directly without float casting.

---

## 4. String & Format Constraints

| Constraint | Applicable Types | Condition | Error Code |
|---|---|---|---|
| `min_length(n)` | `string` | Character length $\ge n$ | `string_too_short` |
| `max_length(n)` | `string` | Character length $\le n$ | `string_too_long` |
| `regex(pat)` | `string` | Must match regex via `nox.regex` | `pattern_mismatch` |
| `in_choices(opts)` | `string` | Must belong to allowed string choices | `choice_mismatch` |
| `email()` | `string` | Valid RFC email format | `invalid_email` |
| `url()` | `string` | Absolute HTTP/HTTPS URL via `nox.url` | `invalid_url` |
| `uuid()` | `string` | 36-character standard UUID | `invalid_uuid` |
| `date()` | `string` | Supported ISO 8601 calendar date (`YYYY-MM-DD`) | `invalid_date` |
| `time()` | `string` | Supported ISO 8601 time (`HH:MM:SS` with optional timezone/fraction) | `invalid_time` |
| `datetime()` | `string` | Supported ISO 8601 combined datetime (`YYYY-MM-DDTHH:MM:SS[Z]`) | `invalid_datetime` |

### Supported ISO 8601 Subset
* **Date**: `YYYY-MM-DD` (four-digit year 0001–9999, two-digit month 01–12, two-digit day 01–31 with February 29 leap year verification).
* **Time**: `HH:MM:SS` (hour 00–23, minute 00–59, second 00–59) with optional fractional seconds (`.sss`) and optional timezone offset (`Z` or `[+-]HH:MM`).
* **Datetime**: `YYYY-MM-DDTHH:MM:SS` (or with space separator) followed by optional timezone.

### Sensitive Data Redaction (`.secret()`)
Fields marked with `.secret()` mask raw values as `[REDACTED]` in error traces and log outputs, preventing credential leaks.

---

## 5. Unknown Fields Policy

Configured via `schema.set_policy(policy)`:
* `POLICY_FORBID` (0, default): Any field present in the input that is not declared in the schema produces an error with code `extra_field`.
* `POLICY_IGNORE` (1): Extra fields in the input are silently omitted and not stored.
* `POLICY_ALLOW` (2): Extra fields are accepted and preserved in `ValidatedData.get_extra_keys()` and can be forwarded to JSON via `Serializer.include_extras(data)`.

---

## 6. Database Row Validation Semantics

Database rows (`nox.db.Row`) passed via `DbAdapter[T].parse_row(row)` or `schema.validate_row(row)` are evaluated against schema rules:
* Unknown columns are governed by `POLICY_FORBID` or `POLICY_ALLOW`.
* Column nullability is verified (`unexpected_null` if a non-nullable column is SQL `NULL`).
* Data types, numeric boundaries, string formats, and choices are strictly checked.
* Cross-field custom validators are executed.
* On violation, `parse_row` raises `ValidationError(errors)`. Non-throwing validation is available via `parse_row_result(row) -> Result[T]` and `validate_row(row) -> ValidationResult`.

---

## 7. Machine Error Codes

| Code | Meaning |
|---|---|
| `invalid_json` | Input string is not valid JSON syntax |
| `expected_object` | Root or nested structure was expected to be an object |
| `missing_field` | A required field/column is missing |
| `unexpected_null` | A non-nullable field/column received `null` |
| `type_mismatch` | Value kind does not match schema field kind |
| `extra_field` | Unknown field/column found under `POLICY_FORBID` |
| `out_of_range` | Numeric bounds violated (`min`/`max`/`ge`/`le`/`gt`/`lt`) |
| `string_too_short` | String length below `min_length` |
| `string_too_long` | String length exceeds `max_length` |
| `invalid_email` | Malformed email address |
| `invalid_url` | Malformed or relative URL |
| `invalid_uuid` | Invalid UUID format |
| `invalid_date` | Invalid ISO 8601 calendar date or leap year mismatch |
| `invalid_time` | Invalid ISO 8601 time format or out-of-range hours/minutes |
| `invalid_datetime` | Invalid ISO 8601 datetime format |
| `pattern_mismatch` | Regex pattern did not match |
| `choice_mismatch` | Value is not in the allowed choices list |
| `array_too_short` | Array length below `min_items` |
| `array_too_long` | Array length exceeds `max_items` |
| `recursion_limit_exceeded` | Input exceeds `max_depth` nesting limit |
| `max_errors_exceeded` | Input exceeds `max_errors` error accumulation cap |
| `custom_validation_error` | Custom validator callback failure |
