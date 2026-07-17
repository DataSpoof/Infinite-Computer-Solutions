"""Pydantic schemas for request/response validation."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(default=None, ge=0, le=150)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema used when creating a user."""


class UserUpdate(BaseModel):
    """Schema used when updating a user. All fields are optional."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    is_active: Optional[bool] = None


class UserOut(UserBase):
    """Schema returned to the client."""

    id: int

    model_config = ConfigDict(from_attributes=True)
