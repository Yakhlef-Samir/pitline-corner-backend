from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)


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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    country: Optional[str] = None
    favorite_f1_team: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuthData(BaseModel):
    """Authentication response data containing token and user info"""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
