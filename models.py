from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
import re


# Task 3.1
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, gt=0)
    is_subscribed: Optional[bool] = False


# Task 5.1
class LoginRequest(BaseModel):
    username: str
    password: str


# Task 5.5
class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        pattern = r'^[a-zA-Z]{2,3}(-[a-zA-Z]{2,})?(,\s*[a-zA-Z]{2,3}(-[a-zA-Z]{2,})?(;\s*q=\d(\.\d)?)?)*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format')
        return v

    class Config:
        populate_by_name = True