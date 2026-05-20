from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    model_config = {"from_attributes: True"}


class URLCreate(BaseModel):
    original_url: str
    expires_days: Optional[int] = 7


class URLOut(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    expires_at: Optional[datetime]
    model_config = {"from_attributes: True"}


class Token(BaseModel):
    access_token: str
    token_type: str