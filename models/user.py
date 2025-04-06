from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    """Modèle Pydantic pour un utilisateur."""
    name: str
    email: EmailStr
    password: str
    is_admin: Optional[bool] = False

class UserLogin(BaseModel):
    """Modèle pour la connexion."""
    email: EmailStr
    password: str