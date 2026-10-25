# Roadmap & Evolution — Noxen

This document tracks the phased development and future releases of **Noxen**.

---

## Completed Milestones

### Phase 0 & Phase 1 — Core MVP (`v0.1.0`)
* [x] Schema & Field DSL (`field_str`, `field_int`, `field_float`, `field_bool`, `field_object`, `field_list`).
* [x] 4 presence modes (`REQUIRED`, `REQUIRED_NULLABLE`, `OPTIONAL`, `OPTIONAL_NULLABLE`).
* [x] Structured errors (`FieldError` with stable codes and `ValidationError(Exception)`).
* [x] Strict unknown field rejection (`POLICY_FORBID`).
* [x] Formats: email, URL, UUID.
* [x] Zero-cost generic model mapper `ModelSchema[T]`.
* [x] Streaming `Serializer` builder.

### Phase 2 & Phase 3 — Ecosystem Adapters & Kinds (`v0.2.0`)
* [x] Aether HTTP response adapter (`json_422`, `json_200`, `json_201`).
* [x] Nyx Database row adapter (`DbAdapter[T]`, `row_to_validated_data`).
* [x] Field aliasing (`.alias("jsonKey")`).
* [x] Allowed choices (`in_choices`, `in_choices_int`).
* [x] Array boundaries (`min_items`, `max_items`).
* [x] Coercion modes (`COERCION_STRICT` vs `COERCION_LAX`).
* [x] Benchmarks suite (640k - 1M+ ops/sec).

### Phase 4 — Security Hardening & Constraints (`v0.3.0`)
* [x] ISO 8601 Date, Time, and Datetime validators (`.date()`, `.time()`, `.datetime()`).
* [x] Sensitive field masking and redaction (`.secret()`).
* [x] Unknown fields preservation policy (`POLICY_ALLOW`).
* [x] JSON Schema Draft 2020-12 reusable definitions with `$defs` and `$ref`.
* [x] Adversarial fuzz and boundary test suite (`tests/fuzz/fuzz_test.nox`).

---

## Future Roadmap (v1.0 & Beyond)

* [ ] **Aura Framework UI Integration**:
  - Direct form state binding and input field validation helpers for Aura web components.
* [ ] **Custom Error Message Formatting**:
  - Configurable error message templates and localization hooks (e.g. English, Turkish, Spanish).
* [ ] **Cross-Platform CI Expansion**:
  - Automated Windows Runner matrix and QBE backend validation.
