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

### Phase 4 — Security Hardening & Constraints (`v0.3.0` – `v0.7.2`)
* [x] ISO 8601 Date, Time, and Datetime validators (`.date()`, `.time()`, `.datetime()`).
* [x] Sensitive field masking and redaction (`.secret()`).
* [x] Unknown fields preservation policy (`POLICY_ALLOW`).
* [x] JSON Schema Draft 2020-12 reusable definitions with `$defs` and `$ref`.
* [x] Adversarial fuzz and boundary test suite (`tests/fuzz/fuzz_test.nox`).
* [x] Bidirectional model serialization (`BidirectionalModel[T]`).
* [x] Automatic schema derivation via `auto_schema("ClassName")` using `nox.reflect`.
* [x] Strict RFC 8259 non-finite float serialization rejection (`NaN`, `Infinity`, `-Infinity`).
* [x] Serializer internal state non-mutation on failed validations (`_record_key` deferred until validation succeeds).
* [x] Exact IEEE 754 negative zero (`-0.0`) sign preservation across JSON serialization and round-trip re-parsing.
* [x] Cycle & recursion detection in schema derivation (`ValueError` on self-referential models).
* [x] Dual-backend (LLVM vs QBE) verification with 100% structured semantic parity markers across all 10 targets.
* [x] Complete cross-platform CI matrix on Ubuntu, macOS, and Windows.

---

## Future Roadmap (v1.0 & Beyond)

* [ ] **Recursive & Self-Referential Model Support (Post-1.0)**:
  - Full support for recursive/cyclic data structures (e.g., category trees, organization charts, comment hierarchies) via JSON Schema Draft 2020-12 `$defs` and `$ref` lazy pointer resolution once runtime ref resolution mechanisms are finalized.
* [ ] **Aura Framework UI Integration**:
  - Direct form state binding and input field validation helpers for Aura web components.
* [ ] **Custom Error Message Formatting & Localization**:
  - Configurable error message templates and localization hooks (e.g. English, Turkish, Spanish).
