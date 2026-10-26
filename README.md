# Noxen

<div align="center">

[![CI](https://github.com/mburakmmm/noxen/actions/workflows/ci.yml/badge.svg)](https://github.com/mburakmmm/noxen/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/mburakmmm/noxen?color=007ec6&label=release)](https://github.com/mburakmmm/noxen/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Nox Toolchain](https://img.shields.io/badge/noxc-2.0.27+-00bcd4.svg)](https://noxlang.com)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-success.svg)](https://github.com/mburakmmm/noxen/actions)
[![JSON Schema](https://img.shields.io/badge/JSON%20Schema-Draft%202020--12-792ee5.svg)](https://json-schema.org)

**Statically typed data modeling, parsing, validation, and high-performance serialization for the [Nox programming language](https://noxlang.com).**

*The idiomatic, reflection-free Pydantic counterpart for the Nox ecosystem with JSON Schema Draft 2020-12 compliance and Aether / Nyx adapters.*

[Quick Start](#quick-start) • [Features](#highlights) • [Benchmarks](#benchmarks) • [Real-World Architecture](#real-world-service-architecture) • [Documentation](#documentation--license) • [Releases](https://github.com/mburakmmm/noxen/releases)

</div>

---

## Overview

**Noxen** brings the useful core of Pydantic to the Nox ecosystem — designed from the ground up as an idiomatic, ahead-of-time compiled, statically typed library with zero runtime reflection overhead or dynamic monkey patching.

```text
       JSON String / Database Row / HTTP Body
                         │
                         ▼
        ┌───────────────────────────────────┐
        │       Noxen Schema Validation     │
        │  • Strict Type Enforcement        │
        │  • Bounds, Regex, Enums & Formats │
        │  • Extra Key & Nullability Policy │
        └───────────────────────────────────┘
                         │
                         ▼
               ValidatedData (Flat)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
   Typed Domain Model                 JSON Output
   (Pure Nox Classes)             (O(1) Strict Stream)
        │                                 ▲
        │                                 │
        ▼                                 │
   Nyx SQLite DB /               Aether HTTP Response
   DbAdapter[T]                  (json_200 / json_201 / json_422)
```

### Highlights

* **Statically Typed Models**: Bind incoming JSON directly into strongly typed Nox classes with compile-time safety via monomorphised generic `ModelSchema[T]`.
* **Strict by Default**: Extra fields are rejected by default (`POLICY_FORBID`), and implicit type coercions are disallowed in strict mode.
* **O(1) Serializer Key Collision Protection**: `Serializer` tracks written property keys using a hash set, ensuring $O(N)$ total complexity and preventing duplicate JSON keys.
* **Output Re-validation**: Separate high-speed direct dump path (1.25M ops/sec) from verified output re-validation (`dump_validated()`) with IEEE 754 precision boundary checks.
* **Nested Models & Multi-Level Arrays**: Validate deeply nested objects and array hierarchies (`Company -> employees[] -> addresses[]`) with pinpoint dot-and-index error paths (`employees[1].addresses[0].city`).
* **Precise Nullability vs Optionality**: Clean distinction between missing keys, explicit nulls, and default fallbacks across 4 distinct presence modes.
* **Format Validators**: Out-of-the-box email, URL (via `nox.url`), and UUID validation.
* **Allowed Choices & Enumerations**: `in_choices` for strings and `in_choices_int` for numeric literals.
* **Field Aliasing**: Support `camelCase` or reserved JSON keys mapped to snake_case model attributes with `.alias("jsonKey")`.
* **Resource & Recursion Limits**: Defend against adversarial payloads with configurable `max_depth` (default 32) and `max_errors` (default 50).
* **Cross-Field Custom Validators**: Register custom callback functions for domain business logic validation.
* **JSON Serialization**: High-performance serialization from typed model instances back to JSON with `Serializer`.
* **JSON Schema Generation**: Export schemas directly to standard JSON Schema Draft 2020-12 specifications with 100% agreement across currently implemented differential test scenarios against Python's official Draft 2020-12 validator.
* **Native Aether & Nyx Adapters**: Ready-to-use HTTP response generators (`json_422`, `json_200`, `json_201`) and database row hydration (`DbAdapter[T]`, `row_to_validated_data`).
* **Dual-Backend Parity (LLVM & QBE)**: Fully tested and verified across both compiler code generation backends with byte-for-byte output equivalence.

---

## Minimum Requirements

* **Compiler**: `noxc 2.0.27` or newer
* **Backend**: LLVM (default) or QBE
* **Platform**: macOS (ARM64/x64), Linux (x64/ARM64), Windows (x64)

---

## Installation

Add Noxen to your project's `nox.json`:

```json
{
  "name": "myapp",
  "entry": "main.nox",
  "requires": [
    {
      "alias": "noxen",
      "repo": "github.com/mburakmmm/noxen",
      "ref": "v0.6.0"
    }
  ]
}
```

Then fetch the dependency:

```sh
noxc fetch
```

Or install via `noxc`:

```sh
noxc add noxen github.com/mburakmmm/noxen --ref v0.6.0
```

---

## Quickstart

```nox
import noxen
from noxen import Schema, ModelSchema, ValidatedData, Result

class User:
    name: str
    age: int
    email: str
    bio: str | None

    def __init__(self: User, name: str, age: int, email: str, bio: str | None) -> None:
        self.name = name
        self.age = age
        self.email = email
        self.bio = bio

# 1. Define schema
user_schema: Schema = Schema("User")
user_schema.field_str("name").min_length(2).max_length(50)
user_schema.field_int("age").min(0.0).max(120.0)
user_schema.field_str("email").email()
user_schema.field_str("bio").optional().nullable()

# 2. Bind typed factory
def make_user(d: ValidatedData) -> User:
    return User(
        d.get_str("name"),
        d.get_int("age"),
        d.get_str("email"),
        d.get_opt_str("bio")
    )

model: ModelSchema[User] = ModelSchema[User](user_schema, make_user)

# 3. Parse and validate JSON
json_input: str = "{\"name\":\"Ada Lovelace\",\"age\":36,\"email\":\"ada@example.com\"}"
res: Result[User] = model.parse_json(json_input)

if res.is_ok:
    user: User = res.unwrap()
    print("Welcome,", user.name, "- Email:", user.email)
else:
    print("Validation failed:", res.errors[0].message)
```

---

## Ecosystem Integrations

### 1. Aether Web Framework Integration

Noxen provides built-in HTTP adapters in `http_adapter.nox` to validate incoming requests and return standard HTTP 422 Unprocessable Entity responses with structured JSON error details:

```nox
import nox.http
from nox.http import HttpRequest, HttpResponse
import models
from models import ModelSchema
import http_adapter
from http_adapter import json_422, json_201

def handle_user_signup(req: HttpRequest, user_model: ModelSchema[UserDto]) -> HttpResponse:
    parsed = user_model.parse_json(req.body)
    if not parsed.is_ok:
        # Returns HTTP 422 with { error, error_count, errors: [...] }
        return json_422(parsed.errors)

    dto = parsed.unwrap()
    # Save user, create response
    return json_201("{\"status\":\"created\"}")
```

### 2. Nyx Database Integration

Noxen includes `db_adapter.nox` for transforming standard `nox.db.Row` instances (from SQLite, PostgreSQL, or MySQL) into strongly typed models:

```nox
import nox.sqlite
from nox.sqlite import Connection
import nox.db
from nox.db import Row
import db_adapter
from db_adapter import DbAdapter

conn: Connection = nox.sqlite.open("production.db")
adapter: DbAdapter[Book] = DbAdapter[Book](book_model)

rows: list[Row] = conn.query("SELECT id, title, author, pages, rating, available FROM books")
books: list[Book] = adapter.parse_rows(rows)

for b in books:
    print(b.title, "by", b.author)
```

---

## Strict Validation & Unknown Fields

By default, Noxen enforces `POLICY_FORBID`. Any unexpected keys in JSON payloads are rejected immediately with machine-readable error code `extra_field`:

```nox
import schema
from schema import Schema, POLICY_FORBID
import core
from core import ValidationResult

s: Schema = Schema("StrictUser")
s.field_str("username")
s.field_int("age")
s.set_policy(POLICY_FORBID)

# Payload containing unexpected field 'isAdmin'
payload: str = "{\"username\":\"ada\",\"age\":30,\"isAdmin\":true}"
res: ValidationResult = s.validate_json(payload)

if not res.is_valid:
    print("Errors:", res.error_summary())
    # Output: Unexpected unknown field: 'isAdmin'
```

---

## Nested Models

```nox
import schema
import models
import core
from schema import Schema
from models import ModelSchema
from core import ValidatedData, Result

class Address:
    city: str
    country: str
    def __init__(self: Address, city: str, country: str) -> None:
        self.city = city
        self.country = country

class Company:
    name: str
    address: Address
    def __init__(self: Company, name: str, address: Address) -> None:
        self.name = name
        self.address = address

addr_schema: Schema = Schema("Address")
addr_schema.field_str("city").min_length(2)
addr_schema.field_str("country").min_length(2)

def make_addr(d: ValidatedData) -> Address:
    return Address(d.get_str("city"), d.get_str("country"))

comp_schema: Schema = Schema("Company")
comp_schema.field_str("name").min_length(1)
comp_schema.field_object("address", addr_schema)

def make_comp(d: ValidatedData) -> Company:
    return Company(d.get_str("name"), make_addr(d.get_object("address")))

comp_model: ModelSchema[Company] = ModelSchema[Company](comp_schema, make_comp)

res: Result[Company] = comp_model.parse_json(
    "{\"name\":\"Acme Corp\",\"address\":{\"city\":\"San Francisco\",\"country\":\"USA\"}}"
)
company: Company = res.unwrap()
print(company.name, "is in", company.address.city)
```

---

## JSON Round-Trip & Automated Serialization

### Automated Schema-Driven Serialization

With `v0.3.2`, you can automatically dump validated data without handwriting manual serializers or using runtime reflection:

```nox
# Dump directly via Schema or ModelSchema
dumped_json: str = user_schema.dump(res.data)
# Or through model:
dumped_json: str = model.dump(res.data)
```

`Schema.dump()` automatically handles:
* Field aliases (wire format matching `.alias("jsonKey")`)
* Nullable fields (`null`) and absent optional fields (omitted)
* Recursively serialized nested models and lists of objects
* Extra attributes under `POLICY_ALLOW` without key collisions

### Programmatic Serialization with Collision Avoidance

For custom control, use `Serializer` to build compact, deterministic JSON:

```nox
import serialization
from serialization import Serializer

s: Serializer = Serializer()
s.str("name", "Ada")
s.int("age", 36)
s.opt_str("bio", None) # Produces "bio": null
# Automatically pass through allowed extras without duplicate keys:
s.include_extras(res.data)
print(s.build())
# Output: {"name":"Ada","age":36,"bio":null}
```

---

## JSON Schema Generation

Export schemas adhering to JSON Schema Draft 2020-12:

```nox
import schema
from schema import Schema

s: Schema = Schema("Product")
s.field_str("name").min_length(2)
s.field_float("price").min(0.01)

schema_json: str = s.to_json_schema()
print(schema_json)
```

---

## Benchmarks

Benchmarked on Apple Silicon (macOS, M-series ARM64) with **`noxc 2.0.27`** using 5,000 operations per benchmark, a 500-iteration warmup phase, 3 trials with median calculation (`median3`), and checksum accumulators to prevent compiler dead code elimination:

| Operation | Iterations | LLVM Throughput | QBE Throughput | LLVM Latency |
|---|---|---|---|---|
| **Flat Model Parsing** | 5,000 | **625,000 ops/sec** (8 ms) | **555,555 ops/sec** (9 ms) | ~1.6 µs/op |
| **Nested Model Parsing** | 5,000 | **555,555 ops/sec** (9 ms) | **500,000 ops/sec** (10 ms) | ~1.8 µs/op |
| **Invalid Payload Rejection** | 5,000 | **1,000,000 ops/sec** (5 ms) | **1,000,000 ops/sec** (5 ms) | ~1.0 µs/op |
| **Full JSON Round-Trip** | 5,000 | **714,285 ops/sec** (7 ms) | **625,000 ops/sec** (8 ms) | ~1.4 µs/op |
| **Deep Hierarchy Parsing (3-Level)** | 5,000 | **454,545 ops/sec** (11 ms) | **384,615 ops/sec** (13 ms) | ~2.2 µs/op |
| **Fast Model Dump (`dump`)** | 5,000 | **1,250,000 ops/sec** (4 ms) | **1,250,000 ops/sec** (4 ms) | ~0.8 µs/op |
| **Validated Model Dump (`dump_validated`)** | 5,000 | **625,000 ops/sec** (8 ms) | **555,555 ops/sec** (9 ms) | ~1.6 µs/op |

Run the benchmarks yourself with either compiler backend:
```sh
# LLVM backend (default)
noxc run --backend llvm benchmarks/run_benchmarks.nox

# QBE backend
noxc run --backend qbe benchmarks/run_benchmarks.nox
```

---

## Feature Support Matrix

| Feature | Status | Notes |
|---|---|---|
| Primitive types (`string`, `int`, `float`, `bool`) | Supported | Strict validation, int precision checks, adaptive relative float epsilon |
| Optional vs Nullable fields | Supported | 4 presence modes (`REQUIRED`, `REQUIRED_NULLABLE`, `OPTIONAL`, `OPTIONAL_NULLABLE`) |
| Default values | Supported | Applied only on missing fields |
| Format validation | Supported | Email, URL (`nox.url`), UUID, Date, Time, Datetime |
| ISO 8601 Date & Time | Supported | `.date()`, `.time()`, `.datetime()` with leap year checks |
| Sensitive Data Redaction | Supported | `.secret()` masks credentials as `[REDACTED]` in errors |
| String length & regex bounds | Supported | `min_length`, `max_length`, `regex` |
| Numeric bounds | Supported | `min`, `max`, `ge`, `le`, `gt`, `lt` |
| Choices & Enums | Supported | `in_choices` (strings), `in_choices_int` (integers) |
| Field Aliases | Supported | `.alias("json_key")` |
| Nested Objects | Supported | `.field_object("address", addr_schema)` |
| Multi-Level Nested Arrays | Supported | `.field_list_schema("employees", emp_schema)` with deep dot-and-index error paths |
| Dual-Backend Parity | Supported | 100% byte-for-byte parity verified across LLVM and QBE |
| Array Bounds | Supported | `min_items`, `max_items` |
| Nested models (`object`) | Supported | Full recursive path validation with `max_depth` caps |
| Arrays / Collections | Supported | Lists of primitives and lists of objects |
| Coercion Modes | Supported | `COERCION_STRICT` (default) & `COERCION_LAX` |
| Unknown fields policy | Supported | `POLICY_FORBID` (default), `POLICY_IGNORE`, `POLICY_ALLOW` |
| Resource Limits | Supported | `max_depth = 32`, `max_errors = 50` caps |
| Custom validator hooks | Supported | Cross-field callbacks via `add_validator` |
| Typed Model Binding | Supported | Zero-cost monomorphised `ModelSchema[T]` |
| JSON Serialization | Supported | Streaming `Serializer` builder |
| JSON Schema Draft 2020-12 | Supported | Standard generator with `$defs` and `$ref` |
| Aether Web Adapter | Supported | `json_422`, `json_200`, `json_201` for `nox.http` |
| Nyx Database Adapter | Supported | `DbAdapter[T]`, `row_to_validated_data` for `nox.db.Row` |

---

## Testing & CI

Run the full test suite with:

```sh
noxc test
```

All 26 unit, integration, and fuzz test suites pass cleanly across Linux, macOS, and Windows CI:

```text
alias_test passed
auto_dump_test passed
bidirectional_model_test passed
choices_test passed
coercion_test passed
custom_validator_test passed
datetime_test passed
db_adapter_test passed
dump_validated_test passed
errors_test passed
fields_test passed
fuzz_test passed
http_adapter_test passed
integer_precision_test passed
json_schema_defs_test passed
json_schema_test passed
limits_test passed
nested_profile_test passed
policy_allow_test passed
property_test passed
secret_redaction_test passed
serialization_test passed
serializer_strict_test passed
unknown_fields_test passed
user_model_test passed
validators_test passed

26 passed, 0 failed (26 total)
```

---

## Documentation & License

* Contributing & Invariants: See [AGENTS.md](AGENTS.md).
* API Reference: See [docs/api.md](docs/api.md).
* Architecture: See [docs/architecture.md](docs/architecture.md).
* Validation Specs: See [docs/validation.md](docs/validation.md).
* Serialization Guide: See [docs/serialization.md](docs/serialization.md).
* Security & Robustness: See [docs/security.md](docs/security.md).
* Compatibility Matrix: See [docs/compatibility.md](docs/compatibility.md).
* Integrations Guide: See [docs/integrations.md](docs/integrations.md).
* Roadmap: See [docs/roadmap.md](docs/roadmap.md).
* Migration Guide: See [docs/migration.md](docs/migration.md).
* License: [MIT](LICENSE)
