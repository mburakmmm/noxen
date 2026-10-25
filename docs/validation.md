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

## 2. Type Checking Matrix

Strict mode is enabled by default. Coercion is forbidden.

| Target Type | Valid JSON Input | Invalid Inputs (produce `type_mismatch`) |
|---|---|---|
| `string` | JSON string `"text"` | Numbers (`123`), Booleans (`true`), Arrays, Objects, Null |
| `int` | JSON integer `42`, `-7` | Fractional numbers (`42.5`), Strings (`"42"`), Booleans (`true`), Null |
| `float` | JSON number `42.5`, `42` | Strings (`"42.5"`), Booleans, Null |
| `bool` | JSON boolean `true`, `false` | Numbers (`1`, `0`), Strings (`"true"`, `"false"`), Null |
| `list[T]` | JSON array `[...]` | Non-array values |
| `object` | JSON object `{...}` | Non-object values |

## 3. Numeric Constraints

| Constraint | Applicable Types | Condition | Error Code |
|---|---|---|---|
| `min(v)` | `int`, `float` | value must be $\ge v$ | `out_of_range` |
| `max(v)` | `int`, `float` | value must be $\le v$ | `out_of_range` |

## 4. String Constraints

| Constraint | Applicable Types | Condition | Error Code |
|---|---|---|---|
| `min_length(n)` | `string` | UTF-8 code point length $\ge n$ | `string_too_short` |
| `max_length(n)` | `string` | UTF-8 code point length $\le n$ | `string_too_long` |
| `pattern(regex)` | `string` | Must match regex via `nox.regex` | `pattern_mismatch` |
| `format("email")` | `string` | Must be a valid email address format | `invalid_email` |
| `format("url")` | `string` | Must be an absolute parseable URL via `nox.url` | `invalid_url` |
| `format("uuid")` | `string` | Must be a 36-character standard UUID | `invalid_uuid` |

## 5. Unknown Fields Policy

Configured via `schema.set_policy(policy)`:
- `Policy.FORBID` (0, default): Any field present in the JSON input that is not declared in the schema produces an error with code `extra_field`.
- `Policy.IGNORE` (1): Extra fields in the JSON input are ignored.

## 6. Custom Validators

A custom validator is registered on the schema:
`validator: (ValidatedData) -> list[FieldError]` (or `(ValidatedData) -> FieldError | None`).
- Executes after all field-level validations succeed.
- Allows cross-field checks (e.g. `start_date <= end_date`, password confirmation matching).

## 7. Machine Error Codes

| Code | Meaning |
|---|---|
| `invalid_json` | Input string is not valid JSON syntax |
| `expected_object` | Root or nested structure was expected to be an object |
| `missing_field` | A required field is missing |
| `unexpected_null` | A non-nullable field received `null` |
| `type_mismatch` | Value kind does not match schema field kind |
| `extra_field` | Unknown field found under `Policy.FORBID` |
| `out_of_range` | Numeric bounds violated (`min`/`max`) |
| `string_too_short` | String length below `min_length` |
| `string_too_long` | String length exceeds `max_length` |
| `invalid_email` | Malformed email address |
| `invalid_url` | Malformed or relative URL |
| `invalid_uuid` | Invalid UUID format |
| `pattern_mismatch` | Regex pattern did not match |
| `custom_validation_error` | Custom validator hook failure |
