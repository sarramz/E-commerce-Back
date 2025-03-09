from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str