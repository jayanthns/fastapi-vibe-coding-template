# Pydantic Guide

This project uses **Pydantic v2** for data validation and settings management.

## Key Concepts

### 1. Schemas (Models)
Schemas define the structure of data.

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int | None = Field(None, ge=0)
```

### 2. Configuration (ConfigDict)
Use `model_config` with `ConfigDict` instead of the nested `Config` class (v1).

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    username: str

    # Allow creating from ORM objects
    model_config = ConfigDict(from_attributes=True)
```

### 3. Validators

#### Field Validators
Validate specific fields.

```python
from pydantic import field_validator

class UserCreate(BaseModel):
    role: str

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ['admin', 'user']:
            raise ValueError('Invalid role')
        return v.lower()
```

#### Model Validators
Validate the entire model (e.g., cross-field validation).

```python
from pydantic import model_validator

class ChangePassword(BaseModel):
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'ChangePassword':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
```

### 4. Settings
We use `pydantic-settings` for environment configuration.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str

    model_config = ConfigDict(env_file=".env")
```

## Best Practices

1. **Explicit Fields**: Use `Field(...)` to provide metadata (description, examples) for API docs.
2. **Type Hints**: Use standard Python type hints (`str | None`, `list[int]`).
3. **Separation**: Keep Request schemas (Create/Update) separate from Response schemas.
4. **Validation**: Put validation logic in Pydantic validators, not in the view/service, to ensure data integrity early.
