from __future__ import annotations

from pydantic import BaseModel, EmailStr


class RegisterUserDTO(BaseModel):
    user_name: str
    password: str
    email: EmailStr
    code_verify: str | None = None


class LoginDTO(BaseModel):
    email: EmailStr
    password: str
