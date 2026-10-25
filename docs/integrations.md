# Noxen Integrations: Aether & Nyx

This guide explains how to integrate **Noxen** with the **Aether** API framework and the **Nyx** full-stack web framework.

---

## 1. Integrating with Aether

[Aether](https://github.com/mburakmmm/aether) is the modern REST API framework for Nox.
Noxen replaces flat DTO schemas with statically typed, validated data models and structured error responses.

### 1.1 In Your `nox.json`

```json
{
  "name": "my_api",
  "entry": "main.nox",
  "requires": [
    { "alias": "aether", "repo": "github.com/mburakmmm/aether", "ref": "master" },
    { "alias": "noxen", "repo": "github.com/mburakmmm/noxen", "ref": "v0.1.0" }
  ]
}
```

### 1.2 Strongly Typed Controller / Handler

```nox
import aether.context
from aether.context import HttpContext
from nox.http import HttpResponse

import schema
import models
import core
from schema import Schema
from models import ModelSchema
from core import ValidatedData, Result

# 1. Define Typed DTO
class CreateUserDto:
    name: str
    email: str
    age: int

    def __init__(self: CreateUserDto, name: str, email: str, age: int) -> None:
        self.name = name
        self.email = email
        self.age = age

# 2. Define Schema & Constraints
create_user_schema: Schema = Schema("CreateUserDto")
create_user_schema.field_str("name").min_length(2).max_length(50)
create_user_schema.field_str("email").email()
create_user_schema.field_int("age").min(18.0).max(120.0)

def make_dto(d: ValidatedData) -> CreateUserDto:
    return CreateUserDto(d.get_str("name"), d.get_str("email"), d.get_int("age"))

create_user_model: ModelSchema[CreateUserDto] = ModelSchema[CreateUserDto](create_user_schema, make_dto)

# 3. Handler with Validation
def handle_create_user(ctx: HttpContext) -> HttpResponse:
    raw_body: str = ctx.body()
    res: Result[CreateUserDto] = create_user_model.parse_json(raw_body)
    
    if not res.is_ok:
        # Return 422 Unprocessable Entity with machine-readable error payload
        headers: dict[str, str] = {"Content-Type": "application/json"}
        return HttpResponse(422, res.errors_json(), headers)

    # Completely type-safe DTO
    dto: CreateUserDto = res.unwrap()
    print("Saving user:", dto.name, dto.email, dto.age)
    
    headers: dict[str, str] = {"Content-Type": "application/json"}
    return HttpResponse(201, "{\"status\":\"created\"}", headers)
```

### 1.3 OpenAPI 3.0 Documentation Export

Since `Schema.to_json_schema()` generates valid JSON Schema Draft 2020-12, it can be passed directly into Aether's OpenAPI documentation metadata:

```nox
schema_spec: str = create_user_schema.to_json_schema()
# Aether registers schema_spec into /openapi.json or Swagger UI
```

---

## 2. Integrating with Nyx

[Nyx](https://github.com/mburakmmm/nyx) is the full-stack web framework for Nox with built-in database ORM and SQLite/MySQL/PostgreSQL drivers.

### 2.1 In Your `nox.json`

```json
{
  "name": "my_nyx_app",
  "entry": "main.nox",
  "requires": [
    { "alias": "nyx", "repo": "github.com/mburakmmm/nyx", "ref": "master" },
    { "alias": "noxen", "repo": "github.com/mburakmmm/noxen", "ref": "v0.1.0" }
  ]
}
```

### 2.2 Model Validation before Database Insertion

```nox
import nyx.model
from nyx.model import Attributes
from nox.sqlite import Connection

import schema
import models
import core
from schema import Schema
from models import ModelSchema
from core import ValidatedData, Result

class UserModel:
    email: str
    username: str
    is_active: bool

    def __init__(self: UserModel, email: str, username: str, is_active: bool) -> None:
        self.email = email
        self.username = username
        self.is_active = is_active

    def to_db_attributes(self: UserModel) -> Attributes:
        attrs: Attributes = nyx.model.attributes()
        nyx.model.set_str(attrs, "email", self.email)
        nyx.model.set_str(attrs, "username", self.username)
        if self.is_active:
            nyx.model.set_str(attrs, "is_active", "1")
        else:
            nyx.model.set_str(attrs, "is_active", "0")
        return attrs

user_schema: Schema = Schema("UserModel")
user_schema.field_str("email").email()
user_schema.field_str("username").min_length(3).max_length(30)
user_schema.field_bool("is_active").default_b(True)

def make_user(d: ValidatedData) -> UserModel:
    return UserModel(d.get_str("email"), d.get_str("username"), d.get_bool("is_active"))

user_binder: ModelSchema[UserModel] = ModelSchema[UserModel](user_schema, make_user)

def save_user_from_json(db: Connection, json_payload: str) -> int:
    res: Result[UserModel] = user_binder.parse_json(json_payload)
    if not res.is_ok:
        raise ValueError("Invalid user input: " + res.errors[0].message)

    u: UserModel = res.unwrap()
    attrs: Attributes = u.to_db_attributes()
    user_id: int = nyx.model.create_attrs(db, "users", attrs)
    return user_id
```
