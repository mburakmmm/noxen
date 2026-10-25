# Noxen

> **Statically typed data modeling, parsing, validation, and serialization for the Nox programming language.**
>
> Maturity status: **v0.1.0 — Stable Core MVP**. Verified against `noxc 2.0.27+`.

---

## Overview

**Noxen** brings the useful core of Pydantic to the Nox ecosystem — designed from the ground up as an idiomatic, ahead-of-time compiled, statically typed library with zero runtime reflection overhead or dynamic monkey patching.

### Highlights

* **Statically Typed Models**: Bind incoming JSON directly into strongly typed Nox classes with compile-time safety.
* **Strict by Default**: Extra fields are rejected by default (`POLICY_FORBID`), and implicit type coercions are disallowed.
* **Nested Models & Collections**: Validate deeply nested objects and arrays with clear dot-and-index error paths (`user.profile.website`, `items[0].id`).
* **Precise Nullability vs Optionality**: Clean distinction between missing keys, explicit nulls, and default fallbacks.
* **Format Validators**: Out-of-the-box email, URL (via `nox.url`), and UUID validation.
* **Cross-Field Custom Validators**: Register custom callback functions for business logic validation.
* **JSON Serialization**: High-performance serialization from typed model instances back to JSON.
* **JSON Schema Generation**: Export schemas directly to standard JSON Schema Draft 2020-12 specifications.

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
      "ref": "v0.1.0"
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
noxc add noxen github.com/mburakmmm/noxen --ref v0.1.0
```

---

## Quickstart

```nox
import schema
import models
import core
from schema import Schema
from models import ModelSchema
from core import ValidatedData, Result

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

## JSON Round-Trip Serialization

Use `Serializer` to build compact, deterministic JSON:

```nox
import serialization
from serialization import Serializer

s: Serializer = Serializer()
s.str("name", "Ada")
s.int("age", 36)
s.opt_str("bio", None) # Produces "bio": null
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

## Feature Support Matrix

| Feature | Status | Notes |
|---|---|---|
| Primitive types (`string`, `int`, `float`, `bool`) | Supported | Strict validation, int precision checks |
| Optional vs Nullable fields | Supported | 4 presence modes (`REQUIRED`, `REQUIRED_NULLABLE`, `OPTIONAL`, `OPTIONAL_NULLABLE`) |
| Default values | Supported | Applied only on missing fields |
| Format validation | Supported | Email, URL (`nox.url`), UUID |
| String length & regex bounds | Supported | `min_length`, `max_length`, `regex` |
| Numeric bounds | Supported | `min`, `max` inclusive |
| Nested models (`object`) | Supported | Full recursive path validation |
| Arrays / Collections | Supported | Lists of primitives and lists of objects |
| Unknown fields policy | Supported | `POLICY_FORBID` (default) & `POLICY_IGNORE` |
| Custom validator hooks | Supported | Cross-field callbacks via `add_validator` |
| Typed Model Binding | Supported | Zero-cost monomorphised `ModelSchema[T]` |
| JSON Serialization | Supported | Streaming `Serializer` builder |
| JSON Schema Draft 2020-12 | Supported | Standard-compliant schema generator |

---

## Testing & CI

Run the full test suite with:

```sh
noxc test
```

All 9 test suites pass without warnings or skips:

```text
nested_profile_test passed
PASSED: .../tests/integration/nested_profile_test.nox
serialization_test passed
PASSED: .../tests/integration/serialization_test.nox
user_model_test passed
PASSED: .../tests/integration/user_model_test.nox
custom_validator_test passed
PASSED: .../tests/unit/custom_validator_test.nox
errors_test passed
PASSED: .../tests/unit/errors_test.nox
fields_test passed
PASSED: .../tests/unit/fields_test.nox
json_schema_test passed
PASSED: .../tests/unit/json_schema_test.nox
unknown_fields_test passed
PASSED: .../tests/unit/unknown_fields_test.nox
validators_test passed
PASSED: .../tests/unit/validators_test.nox

9 passed, 0 failed (9 total)
```

---

## Contributing & License

* Contributing & Invariants: See [AGENTS.md](AGENTS.md).
* Architecture: See [docs/architecture.md](docs/architecture.md).
* Validation Specs: See [docs/validation.md](docs/validation.md).
* Compatibility Matrix: See [docs/compatibility.md](docs/compatibility.md).
* License: [MIT](LICENSE)
