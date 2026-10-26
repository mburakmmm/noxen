# Serialization Guide — Noxen

Noxen includes an ahead-of-time compiled, high-performance streaming serializer (`serialization.Serializer`) built directly on `nox.json.JsonWriter`.

---

## 1. Design Principles

1. **Zero Dynamic Inspection**: Nox is statically typed; serialization does not use runtime reflection or hidden monkey patching.
2. **Explicit Contracts**: You write an idiomatic companion serializer or method for your models.
3. **Deterministic Ordering**: Fields are emitted in the exact order declared by your serialization statements.
4. **Clean Null Handling**: Differentiates between omitted fields and explicit JSON `null`.
5. **No Code Execution**: Serializer performs purely mechanical formatting without evaluating arbitrary expressions.

---

## 2. Basic Serialization

```nox
import serialization
from serialization import Serializer

s: Serializer = Serializer()
s.str("title", "Mechanical Keyboard")
s.float("price", 149.99)
s.int("stock", 25)
s.bool("is_available", True)

result_json: str = s.build()
# {"title":"Mechanical Keyboard","price":149.99,"stock":25,"is_available":true}
```

---

## 3. Optional & Nullable Values

Optional fields can be handled conditionally or serialized as explicit `null`:

```nox
s: Serializer = Serializer()
s.str("name", "Alice")

# If bio is None, emits "bio": null
s.opt_str("bio", None)

# If website is provided, emits "website": "https://..."
s.opt_str("website", "https://example.com")

print(s.build())
# {"name":"Alice","bio":null,"website":"https://example.com"}
```

---

## 4. Collections & Arrays

`Serializer` provides built-in methods for primitive arrays:

```nox
s: Serializer = Serializer()
s.str("project", "Noxen")
s.list_str("tags", ["compiler", "validation", "pydantic"])
s.list_int("version_numbers", [0, 2, 0])
```

---

## 5. Nested Models & Composition

Nested models can be serialized by nesting serializers using `raw_json`:

```nox
# Address serializer
addr_s: Serializer = Serializer()
addr_s.str("city", "San Francisco")
addr_s.str("country", "USA")

# Parent serializer
user_s: Serializer = Serializer()
user_s.str("name", "Bob")
user_s.raw_json("address", addr_s.build())

print(user_s.build())
# {"name":"Bob","address":{"city":"San Francisco","country":"USA"}}
```

---

## 6. Automated Schema & Bidirectional Model Serialization (Reflection-Free)

Starting in `v0.3.2` and perfected in `v0.4.0`, Noxen supports automated serialization directly from validated models and schemas using `dump(data: ValidatedData) -> str` and typed `BidirectionalModel[T]`:

```nox
import noxen
import models
from noxen import Schema, ValidatedData
from models import ModelSchema, BidirectionalModel

class User:
    id: int
    name: str
    bio: str | None

    def __init__(self, id: int, name: str, bio: str | None) -> None:
        self.id = id
        self.name = name
        self.bio = bio

user_schema: Schema = Schema("User")
user_schema.field_int("id")
user_schema.field_str("name").alias("full_name")
user_schema.field_str("bio").nullable().optional()

def make_user(d: ValidatedData) -> User:
    return User(d.get_int("id"), d.get_str("name"), d.get_opt_str("bio"))

def unparse_user(u: User) -> ValidatedData:
    d: ValidatedData = ValidatedData()
    d.set_int("id", u.id)
    d.set_str("name", u.name)
    d.set_opt_str("bio", u.bio)
    return d

user_model: ModelSchema[User] = ModelSchema[User](user_schema, make_user)
user_bi: BidirectionalModel[User] = BidirectionalModel[User](user_model, unparse_user)

# Parse from JSON into typed User object
user: User = user_bi.parse_json("{\"id\": 42, \"full_name\": \"Grace Hopper\", \"bio\": null}").unwrap()

# Dump typed User object directly back to JSON wire format (with alias 'full_name'!)
dumped_json: str = user_bi.dump(user)
# {"id":42,"full_name":"Grace Hopper","bio":null}
```

### Key Collision Protection with `strict()` and `POLICY_ALLOW`

`Serializer.strict() -> Serializer` activates strict key checking. Any attempt to write a duplicate key raises `ValueError` immediately.

When `POLICY_ALLOW` is enabled, extra properties present in `ValidatedData` are serialized automatically without duplicate key bugs. `Serializer` tracks all written keys (`has_written_key`) so that extra properties colliding with defined schema fields are safely ignored during output generation.

---

## 7. Performance

Because `Serializer` streams directly to Zig's underlying string buffer via `JsonWriter` and `ValidatedData` utilizes a non-cyclic flat representation:
* Generates over **1,250,000 serialized documents per second** on Apple Silicon ARM64.
* Does not construct intermediate dynamic hash tables.
* Minimizes heap allocations with zero garbage collector lock contention.
