from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    password_confirm: str


class UserResponse(UserBase):
    id: int
    tier: str = "freemium"
    is_active: bool = True
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserPublic(BaseModel):
    """Public user information returned in API responses"""

    id: int
    email: EmailStr
    tier: str

    model_config = ConfigDict(from_attributes=True)


class AuthData(BaseModel):
    """Authentication response data containing token and user info"""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
