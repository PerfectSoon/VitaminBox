from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.core.types import UserType


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str]


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserOut(UserBase):
    id: int
    role: UserType

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserAuth(BaseModel):
    email: EmailStr
    password: str
