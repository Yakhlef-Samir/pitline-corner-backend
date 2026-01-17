from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class UserPublic(BaseModel):
    """Public user information returned in API responses"""

    id: int
    email: EmailStr
    tier: str

    class Config:
        from_attributes = True


class AuthData(BaseModel):
    """Authentication response data containing token and user info"""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
