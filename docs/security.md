# Security & Robustness Guide — Noxen

> **Threat Model**: All external input (JSON strings, query parameters, network payloads) must be treated as hostile and untrusted until fully validated by Noxen.

---

## 1. Resource Limits & Denial-of-Service Defense

### Recursion Depth Caps (`max_depth`)
* **Risk**: Adversarial payloads containing deeply nested objects (`{"a":{"a":{"a":...}}}`) can cause thread stack overflow.
* **Defense**: Noxen defaults to `max_depth = 32`. Nested models automatically inherit and propagate parent depth limits.
* **Behavior**: If depth is exceeded, validation halts immediately and reports `recursion_limit_exceeded`.

### Error Accumulation Caps (`max_errors`)
* **Risk**: Adversarial payloads containing thousands of invalid keys can consume unbounded memory accumulating error objects.
* **Defense**: Noxen defaults to `max_errors = 50`.
* **Behavior**: Once the cap is reached, validation terminates and appends `max_errors_exceeded`.

---

## 2. Sensitive Data Redaction (`.secret()`)

* **Risk**: Passwords, API tokens, session secrets, and payment credentials must never appear in logs, error traces, or API responses.
* **Defense**: Mark sensitive fields with `.secret()`.
* **Behavior**: When validation fails on a secret field (e.g. failing regex, choice, or length), Noxen masks the `actual` field as `"[REDACTED]"`.

```nox
s: Schema = Schema("Auth")
s.field_str("api_key").secret().min_length(16)
```

---

## 3. Strict Unknown Field Policy (`POLICY_FORBID`)

* **Risk**: Mass assignment vulnerabilities where malicious clients inject unauthorized attributes (e.g. `{"isAdmin": true}`).
* **Defense**: Noxen defaults to `POLICY_FORBID`. Any unexpected key in the JSON payload immediately fails validation with `extra_field`.

---

## 4. No Arbitrary Code Execution

* Noxen does not implement Python-style `eval`, `exec`, dynamic imports, or runtime class generation.
* JSON parsing relies solely on Nox's native standard library (`nox.json`), which parses text strictly into standard tree values.
* Custom validators are purely compiled Nox function pointers `(ValidatedData) -> list[FieldError]`.

---

## 5. Input Validation vs Output Sanitization

* **Important Note**: Validating a field (e.g., ensuring a string is an email or alphanumeric) is **not** HTML sanitization or SQL escaping.
* When rendering user input in web browsers, use proper HTML entity escaping.
* When inserting into SQL databases, always use parameterized queries with `Statement.bind_*` or Nyx ORM models.
