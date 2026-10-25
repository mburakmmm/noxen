# AGENTS.md — Noxen

> Binding engineering instructions for AI coding agents working on **Noxen**, a standalone, statically typed data modeling, parsing, validation, and serialization library for the Nox programming language.

## 0. Mission and authority

Build Noxen as the idiomatic Nox counterpart to the *useful core* of Pydantic, **not** as a Python port or a new language runtime.

- Language repository: `https://github.com/mburakmmm/nox-lang`
- Language documentation: `https://noxlang.com`
- Noxen is an independent package; Nyx, Aether, and Aura are optional consumers, never mandatory dependencies.
- Deliver a small, reliable, well-documented, well-tested library before expanding features.
- This file applies to every agent, subagent, and generated change in this repository.
- Explicit user requirements outrank optional roadmap suggestions; security and correctness requirements remain mandatory.
- Never claim an API, syntax form, compiler capability, platform, or command exists without checking the installed Nox toolchain, its documentation, or a compiling example.

### Required discovery before coding

1. Read this entire file and inspect the existing Noxen repository.
2. Read the current Nox `README.md`, `AGENTS.md`, `VERSIONING.md` (when available), language reference, stdlib documentation, package documentation, and relevant examples. Follow Nox's own invariants. Its compiler repository AGENTS.md governs changes to Nox itself, not permission to alter the compiler from this project.
3. Record installed `noxc` version, available backends/targets, actual package layout, module imports, test commands, and CI.
4. Inspect `nox.validate`, `nox.json`, type definitions, generics, reflection/metadata support (if any), exceptions, error handling, and existing model-like abstractions. Avoid duplicating stdlib facilities.
5. Write `docs/compatibility.md` with verified capabilities, exact evidence, unsupported assumptions, and decisions.
6. Prototype and **compile** one tiny model with two fields, one nested model, and JSON round-trip before committing to an architecture.
7. If the necessary language feature is missing, use the smallest idiomatic supported alternative. Do not silently invent decorators, runtime reflection, annotations, `Any`, macros, dynamic attributes, or code generation hooks.

## 1. Non-negotiable principles

1. **Nox-first.** All public APIs must use real, currently supported Nox syntax and types. All normal library behavior should be implemented in `.nox`; native shims only when strictly necessary and justified.
2. **Static typing always.** Never circumvent Nox's mandatory static typing with fake dynamic objects or unchecked casts.
3. **No visible ownership annotations.** Preserve Nox's automatic memory management and normal value lifetimes.
4. **No compiler fork or changes** without explicit user approval. A missing feature is not permission to modify `nox-lang`.
5. **No hidden mutable global state.** Validation state, context, and configuration should be explicit or immutable.
6. **Deterministic behavior.** Same input, schema, and options must produce the same result and ordered errors.
7. **No arbitrary code execution** during parsing or deserialization.
8. **Strict by default.** Never silently coerce data in strict mode. Coercion, if supported, is explicit and documented.
9. **No silent data loss.** Unknown fields, duplicate keys, nulls, and serialization omissions follow documented policies.
10. **No false success.** Every public API requires executable tests and an example that compiles on supported toolchains.
11. **No broad dependencies.** Prefer stdlib; external dependencies require justification and version constraints.
12. **No Python runtime dependency.** Python may be used only for optional developer-side comparisons, never for Noxen's runtime.
13. **No security shortcuts.** Bound input sizes and nesting, redact secrets, and treat JSON/schema/input as untrusted.
14. **Compatibility is a feature.** Public API changes require migration notes, versioning, and tests.
15. **Never hide failures.** Do not weaken tests, skip checks silently, or label incomplete work “production-ready”.

## 2. Scope and exclusions

### Core scope

- Typed model definitions and schema representation.
- Validation of primitives, collections, nested models, optional/nullable fields.
- Clear, structured, machine-readable validation errors.
- Explicit strict and opt-in conversion modes.
- Model ↔ JSON conversion using verified Nox JSON APIs.
- Defaults, field constraints, custom validators.
- JSON Schema generation where accurately representable.
- Integration adapters for Nyx/Aether **only after** a stable independent core exists.

### Out of scope for v1

- Runtime-generated classes, Python-style metaclasses, `setattr`, `exec`, eval, dynamic imports.
- Unverified decorator syntax or automatic runtime reflection.
- ORM/database drivers, HTTP routing, authentication, UI widgets.
- Full Pydantic compatibility or CPython interoperability.
- Network access, filesystem access, arbitrary shell commands during validation.
- Compiling schema definitions into native machine code.
- Runtime plugin loading or third-party validator execution from untrusted schema.
- Silent or implicit type conversions.
- Reimplementation of JSON parsing when stdlib already provides it.

**Design rule:** Validation, conversion, serialization, and schema generation are separate operations with explicit contracts.

## 3. Architecture: capability-gated, not speculative

Start with a working **schema-driven validation core**. Add typed-model ergonomics only to the extent Nox can express them safely today.

Recommended logical components (actual paths must follow verified Nox package conventions):

```text
noxen/
  AGENTS.md
  README.md
  LICENSE
  CHANGELOG.md
  docs/
    compatibility.md
    architecture.md
    api.md
    validation.md
    serialization.md
    security.md
    roadmap.md
    migration.md
  src/                   # adapt to actual Nox package layout
    noxen/
      core/
      fields/
      errors/
      json/
      schema/
      validators/
      serialization/
  tests/
    unit/
    integration/
    regression/
    fixtures/
  examples/
    basic_model.nox
    nested_model.nox
    strict_validation.nox
    json_roundtrip.nox
    custom_validator.nox
  benchmarks/
  .github/workflows/
```

Do not create empty directories/files merely to mimic this tree.

### Layer responsibilities

- `core`: schema and model contracts, configuration, validation orchestration.
- `fields`: field definitions, required/default/nullable/optional semantics.
- `validators`: built-in constraints, custom validation hooks.
- `errors`: error types, paths, stable codes, human-readable messages.
- `json`: adapt to the Nox stdlib JSON parser/serializer.
- `serialization`: controlled output, exclusion and alias policies.
- `schema`: supported JSON Schema output and compatibility limitations.
- `integration`: optional adapters in separate packages or modules that do not pull frameworks into the core.

**Dependency direction:** adapters → public Noxen API → core → Nox stdlib. No circular dependencies.

## 4. API design requirements

The following names are **conceptual targets**, not verified Nox declarations:

- `Model` or equivalent typed schema contract.
- `Field` metadata/configuration.
- `ValidationResult[T]` or Nox-native typed success/failure mechanism.
- `ValidationError` with ordered list of `FieldError`.
- `validate(...)`, `parse_json(...)`, `to_json(...)`, `to_dict(...)` equivalents.
- `schema_json(...)` / `json_schema(...)` when supported.

Before adopting any name, compile a proof-of-concept and document the exact signature.

### Preferred developer experience

A user should be able to:

1. Declare a typed model/schema with fields.
2. Validate structured input without unsafe casts.
3. Obtain a typed result or structured errors.
4. Serialize valid values to JSON.
5. Parse serialized values back and preserve semantics.

If direct typed-class construction from runtime JSON requires unavailable reflection, implement an explicit mapper or generated code **only if supported and tested**. A schema-only MVP is acceptable; fake typed-model support is not.

### Error contract

Each error must expose, as supported by the language:

- Stable machine code (e.g. `type_mismatch`, `missing_field`, `invalid_format`, `out_of_range`).
- Location path as ordered field names/array indices; support root errors.
- Expected type or constraint, when safe.
- Actual type/category, when safe.
- Human-readable message.
- Optional sanitized context; never embed raw credentials by default.

Example conceptual error:

```json
{
  "errors": [
    {
      "path": ["profile", "age"],
      "code": "out_of_range",
      "message": "Value must be at least 0"
    }
  ]
}
```

Never promise byte-for-byte error compatibility with Pydantic.

## 5. Validation semantics (specify before implementation)

Create a decision table in `docs/validation.md` and tests for every case below.

### Presence and nullability

- **Missing** means no key exists; **null** means a key exists with JSON null.
- Required fields reject missing values.
- Nullable fields accept null, but do not automatically become optional/missing.
- Optional fields may be absent according to explicit policy; their representation must be compatible with Nox types.
- Defaults apply only on missing unless a separately documented policy says otherwise.
- Never share mutable default objects across model instances.
- Defaults themselves must be validated.
- An explicitly present invalid value must not be replaced by a default.

### Primitive types

- Strings: distinguish string from number/bool/null; validate length in a documented unit (Unicode code points, UTF-8 bytes, etc.).
- Integers: reject fractional values, overflow, and out-of-range conversion.
- Floats: define treatment of integers, NaN, infinity, negative zero, and precision.
- Booleans: do not accept `"true"`, `1`, or other representations in strict mode.
- Null: only accepted when allowed.
- Arrays: validate every element with stable index paths.
- Objects: validate keys, missing/extra fields, and nested structures.
- Enums/literals: exact match by default.
- Dates, times, URLs, emails: optional validators; document which standard/subset is implemented.

### Constraints

- Numeric min/max and inclusive/exclusive bounds.
- String min/max length, regex matching if supported.
- Array min/max length and element constraints.
- Literal/enum membership.
- Cross-field validators and custom field validators in later phases.

### Unknown fields

Support a clearly configured policy:

- `forbid`: report unexpected fields.
- `ignore`: omit unexpected fields.
- `allow`: preserve them only when the typed representation and serialization can do so safely.

Choose and document one stable default; **prefer `forbid` for the first stable release**.

### Coercion

- Strict mode is the default.
- If a conversion mode is implemented, define an explicit type-by-type conversion matrix.
- Reject ambiguous conversions.
- Never coerce booleans into integers or vice versa implicitly.
- Avoid locale-dependent numeric parsing.
- Conversion errors must be distinguishable from validation errors where practical.

### Error accumulation

- Prefer collecting independent field errors in schema order.
- Define and test fail-fast behavior if offered.
- Set configurable caps for error count to prevent unbounded allocation.
- Stable ordering is part of the public contract.

## 6. JSON parsing and serialization

Use verified `nox.json` APIs; do not write a replacement parser without compelling evidence.

- Define maximum input byte size, nesting depth, array/object size, and error count.
- Reject malformed UTF-8 where required by the underlying representation.
- Define duplicate JSON key behavior explicitly; reject by default **if the underlying parser exposes duplicates**, otherwise document the limitation and consider a verified pre-parse solution.
- Preserve numeric correctness; never round-trip large integers through imprecise floats unnoticed.
- JSON `null`, missing fields, empty arrays, and empty objects must remain distinct.
- Ensure string escaping and Unicode handling are correct.
- Specify canonical ordering only if deliberately supported; otherwise document deterministic library-controlled ordering.
- Do not serialize secrets into logs/errors.
- Detect or reject unsupported recursive/cyclic structures rather than looping indefinitely.
- If schema serialization is unsupported for a custom validator, report a clear unsupported feature rather than inventing semantics.
- JSON round-trip tests must check semantic equivalence, not only successful parsing.

## 7. JSON Schema policy

Target JSON Schema Draft 2020-12 **only for the subset correctly implemented**; if that draft cannot be represented faithfully, publish a clearly named supported subset rather than a false compliance claim.

Cover when implemented:

- `type`, `properties`, `required`, `additionalProperties`.
- `$defs`/`$ref` for reusable and recursive models.
- `items`, `minItems`, `maxItems`.
- `minimum`, `maximum`, exclusive bounds.
- `minLength`, `maxLength`, `pattern`.
- `enum`, `const`, `default`, `description`, `title`.
- Nullability and nested models.

Do not emit constraints that the runtime cannot enforce without documenting the mismatch. Test generated schemas against expected fixtures and, where possible, an independent standards-compliant validator.

## 8. Security and robustness

All external data is hostile until validated.

- Resource limits for input length, depth, number of fields, collection elements, and errors.
- No catastrophic regex behavior without time/complexity limits or documented restrictions.
- No regex-based email validation advertised as complete RFC compliance.
- Do not execute code from JSON or JSON Schema.
- Prevent stack exhaustion on deeply nested inputs; enforce depth caps.
- No unbounded recursion on self-referential schemas.
- Never echo entire sensitive payloads into exceptions.
- Document the distinction between validation and sanitization; validated text is not automatically safe for HTML/SQL/shell.
- No network fetch of `$ref` or remote schema by default.
- Native/FFI dependencies, if unavoidable, require explicit review and isolation.
- Fuzz malformed JSON, Unicode edge cases, deep nesting, large numbers, and adversarial lengths where tooling permits.

## 9. Performance and memory

Correctness precedes speed. Do not invent performance claims.

- Establish baselines for flat objects, nested objects, arrays, invalid payloads, and JSON round-trips.
- Benchmark cold/warm paths separately if caching exists.
- Prefer immutable, reusable schema definitions and avoid rebuilding metadata for every instance.
- Do not add hidden mutable caches.
- Minimize copies where Nox APIs permit, without breaking value lifetimes.
- Never trade validation correctness for speed.
- Include memory allocation observations when measurable.
- Record compiler version, backend, optimization flags, platform, input sizes, and repetitions with benchmark results.
- Avoid unsupported claims of being faster than Pydantic/Python.

## 10. Testing requirements

For every public API, include:

1. Valid input.
2. Invalid input.
3. Missing vs explicit null.
4. Boundary conditions.
5. Nested path errors.
6. Unicode and escaping where relevant.
7. Serialization round-trip.
8. Deterministic output/errors.
9. Resource limit behavior.
10. Regression test for each fixed bug.

### Mandatory test matrix

- Strings, booleans, signed integers, floating point.
- Integer overflow, float edge cases, precision.
- Empty/missing/null/default values.
- Lists of primitives and lists of nested objects.
- Deeply nested objects and recursion limits.
- Unknown fields: forbid/ignore/allow as implemented.
- Invalid JSON and duplicate keys as supported.
- Unicode, embedded null characters, escapes.
- Custom validator success/failure and error propagation.
- Multiple independent errors and stable ordering.
- Schema generation consistency.
- Public API examples compile.
- Supported OS/backend combinations.

Use the actual `noxc` test/build commands discovered in this repository. **Do not invent CLI flags**. Save verified commands in `docs/compatibility.md`.

For any claimed platform support, run CI on that platform or explicitly mark it unverified. Prefer Linux, macOS, and Windows when available. For compiler backend parity, test all verified supported backends and document exceptions.

No skipping, deleting, weakening, or rewriting tests merely to make CI green.

## 11. Documentation standards

Documentation and examples must be written in English for a globally usable package; Turkish supplementary docs are welcome.

`README.md` must contain:

- One-sentence description and current maturity status.
- Minimum verified Nox version.
- Installation instructions matching the actual Nox package registry/manager.
- Compiling quick-start example.
- Strict validation example.
- Nested model example.
- Error handling example.
- JSON round-trip example.
- Feature support matrix and explicit limitations.
- License, contribution guide, and changelog links.

All snippets must be exercised in CI when feasible. Never publish hypothetical syntax as executable code. If illustrating future syntax, label it **PSEUDOCODE — NOT IMPLEMENTED**.

## 12. Package and versioning

- Use the verified Nox package manifest format and registry conventions.
- Keep runtime dependencies minimal.
- Follow Semantic Versioning after v1.0; pre-1.0 changes must still be documented.
- Pin or constrain compatible compiler versions.
- Track compatibility against Nox 2.x and newer versions only after verification.
- Public exports should be intentional; internal helpers remain internal.
- Generate changelog entries for meaningful changes.
- Never publish a release or change the package registry without explicit user authorization.
- Never claim Noxen is part of the Nox standard library.

## 13. Implementation phases and exit criteria

### Phase 0 — Feasibility and specification
- Inspect Nox compiler, stdlib, package tooling, and existing validation utilities.
- Produce capability matrix and compile minimal proofs.
- Specify typed-model strategy, nullability, errors, JSON limitations, and version requirements.
- Exit: verified compiling proof, documented API plan, no invented language features.

### Phase 1 — Core MVP
- Basic schema representation and field declarations.
- Required/optional/nullable/default semantics.
- Primitive type checks and nested objects/lists.
- Structured errors and strict mode.
- JSON parsing/serialization using stdlib.
- Exit: complete tests for implemented contracts and working examples.

### Phase 2 — Ergonomics
- Typed-model mapping with a **verified** Nox mechanism.
- Numeric/string/collection constraints.
- Custom validators and stable error customization.
- Unknown-field policies.
- Exit: nested typed model example compiles and round-trips.

### Phase 3 — Interoperability
- JSON Schema subset generation.
- Aliases, controlled serialization/exclusion if justified.
- Opt-in conversion matrix.
- More advanced types only when robust.
- Exit: schema fixtures and compatibility tests pass.

### Phase 4 — Integration and hardening
- Optional Aether/Nyx adapters, no core dependency.
- Fuzz/property tests and performance benchmarks.
- Cross-platform CI, docs, API review.
- Exit: documented support matrix and release checklist.

**Do not jump phases** to implement attractive extras while the core is broken.

## 14. Agent workflow for every task

1. Restate the exact task and acceptance criteria.
2. Inspect affected source files and related tests.
3. Check language/API feasibility against verified references.
4. Identify compatibility and security implications.
5. Make the smallest coherent change.
6. Add tests **before or alongside** implementation.
7. Run formatting, compiler, tests, examples, and applicable CI checks.
8. Review changed files for scope creep, accidental API breaks, dead code, unbounded allocations, and secrets.
9. Update documentation and changelog when behavior changes.
10. Report exact changed files, executed commands, pass/fail results, unsupported cases, and next steps.

### Failure protocol

If blocked by compiler limitations, missing docs, missing toolchain, or incompatible APIs:

- Stop claiming the feature is complete.
- Record a minimal reproducible example.
- State the precise missing capability.
- Propose the smallest supported fallback.
- Ask the user before modifying Nox itself or materially changing public behavior.

Never invent test output, benchmark numbers, compiler capabilities, or successful CI.

## 15. Collaboration and repository hygiene

- Preserve existing user changes; do not overwrite unrelated work.
- Keep PRs focused and reviewable.
- Do not force-push, reset branches, delete files, or rewrite history without permission.
- Do not add credentials, tokens, or personal data to the repository.
- Do not use broad auto-formatting that touches unrelated files.
- Prefer small, composable modules and explicit dependencies.
- Update tests with fixes; document why the bug occurred.
- Use clear commit messages: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `perf:`.
- No generated build artifacts committed unless the repo explicitly requires them.

## 16. Definition of Done

A feature is complete **only if all applicable items are true**:

- [ ] Implementation uses verified Nox syntax and supported APIs.
- [ ] Public API and semantics are documented.
- [ ] Success, failure, boundary, and regression tests pass.
- [ ] Example code compiles and runs.
- [ ] Strict typing and Nox ownership invariants remain intact.
- [ ] Resource limits and sensitive error output are considered.
- [ ] No unintended framework/runtime dependency.
- [ ] No compiler changes without explicit approval.
- [ ] Relevant OS/backend checks pass or are marked unverified.
- [ ] No test skips or misleading completion claims.
- [ ] Changelog/compatibility documentation is updated.
- [ ] Final report includes real commands and observed results.

## 17. First task for an autonomous coding agent

**Do not start by implementing all of Pydantic.**

1. Audit the current Nox toolchain and `nox.validate`/`nox.json` behavior.
2. Create `docs/compatibility.md`, `docs/architecture.md`, and `docs/validation.md`.
3. Design the smallest typed/schema-driven API Nox can compile today.
4. Implement and test one `User` model with `name: str`, `age: int`, and one optional/nullable field, using *verified syntax*.
5. Add a nested `Profile` model, invalid-input errors, and a JSON round-trip.
6. Build a minimal CI job using real commands.
7. Report exactly what works, what does not, and the proposed Phase 1 backlog.

**Quality bar:** A small, real, compilable Noxen library is better than a large repository of plausible but non-compiling Nox code.
