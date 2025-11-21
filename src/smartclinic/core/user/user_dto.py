from typing import Literal

from pydantic import BaseModel, EmailStr


class UserDTO(BaseModel):
    id: str
    user_name: str
    email: EmailStr
    role: str


class UpdateUserRoleDTO(BaseModel):
    role: Literal["user", "doctor"]
