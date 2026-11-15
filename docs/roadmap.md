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

### Phase 4 — Security Hardening & Constraints (`v0.3.0` – `v0.9.0`)
* [x] ISO 8601 Date, Time, and Datetime validators (`.date()`, `.time()`, `.datetime()`), `nox.regex` full-match engine, TOML/YAML support, and multiple-inheritance Mixins.

### Phase 5 — Nox 2.1.186 Precision, Ergonomics & Multi-Protocol Adapters (`v0.10.0` – `v0.11.0`)
* [x] Signed 64-bit integers + opt-in `.safe_int53()` guard & single-pass object field index in `Schema.validate_at`.
* [x] Exact `Decimal` & `BigInt` support across schemas, bounds, scale checks, JSON serialization, and Draft 2020-12 output.
* [x] `nox.unicode` string sanitizers/normalizers, `uuid7()`, `UUIDMixin.generate_v4/v7()`, and IANA `.timezone()` validator.
* [x] Discriminated `UnionSchema` (`oneOf` + `discriminator`) and exhaustive `enum ValidationOutcome[T]`.
* [x] `@dataclass` & class-level metadata decorators via `nox.reflect`.
* [x] `yield`-based `stream_ndjson()` generators, RFC 4180 `csv_adapter.nox`, enhanced `nox.web` HTTP helpers, `nox.property` shrinking tests, and `wasm32-wasi` core verification.
* [x] Optional standalone `yyjson_adapter.nox`, `pcre2_adapter.nox`, and binary `protobuf_adapter.nox`.

---

## Future Roadmap (v1.0 & Beyond)

* [ ] **Recursive & Self-Referential Model Support (Post-1.0)**:
  - Full support for recursive/cyclic data structures (e.g., category trees, organization charts, comment hierarchies) via JSON Schema Draft 2020-12 `$defs` and `$ref` lazy pointer resolution once runtime ref resolution mechanisms are finalized.
* [ ] **Aura Framework UI Integration**:
  - Direct form state binding and input field validation helpers for Aura web components.
* [ ] **Custom Error Message Formatting & Localization**:
  - Configurable error message templates and localization hooks (e.g. English, Turkish, Spanish).
