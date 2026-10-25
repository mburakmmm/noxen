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

## 6. Automated Schema Serialization (Reflection-Free)

Starting in `v0.3.2`, Noxen supports automated serialization directly from validated models and schemas using `dump(data: ValidatedData) -> str`:

```nox
import schema
from schema import Schema

# 1. Define schema with fields, aliases, and nested structures
s: Schema = Schema("User")
s.field_int("id")
s.field_str("name").alias("full_name")
s.field_str("bio").nullable().optional()

# 2. Validate input
res = s.validate_json("{\"id\": 42, \"full_name\": \"Grace Hopper\", \"bio\": null}")

# 3. Automatically dump validated data back to JSON wire format
output_json: str = s.dump(res.data)
# {"id":42,"full_name":"Grace Hopper","bio":null}
```

### Key Collision Protection with `POLICY_ALLOW`

When `POLICY_ALLOW` is enabled, extra properties present in `ValidatedData` are serialized automatically without duplicate key bugs. `Serializer` tracks all written keys (`has_written_key`) so that extra properties colliding with defined schema fields are safely ignored during output generation.

---

## 7. Performance

Because `Serializer` streams directly to Zig's underlying string buffer via `JsonWriter`:
* Generates over **780,000 JSON documents per second** on Apple Silicon ARM64.
* Does not construct intermediate dynamic hash tables.
* Minimizes heap allocations.
