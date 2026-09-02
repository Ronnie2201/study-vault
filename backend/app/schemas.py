from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr  # Validates email format automatically
    password: str = Field(min_length=8, max_length=72)  # bcrypt limit
    full_name: str = Field(min_length=2, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets minimum security requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to client."""

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    # Pydantic v2 style
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for data extracted from JWT token."""

    user_id: int | None = None
    email: str | None = None


class SubjectCreate(BaseModel):
    """Schema for creating a subject."""

    name: str = Field(min_length=1, max_length=200)
    code: str | None = Field(None, max_length=50)
    color: str = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")


class SubjectResponse(BaseModel):
    """Schema for subject data returned to client."""

    id: int
    name: str
    code: str | None
    color: str
    created_at: datetime

    # Pydantic v2 style
    model_config = ConfigDict(from_attributes=True)
