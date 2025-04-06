from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    id: Optional[str] = Field(default=None)  # Pas besoin d'alias "_id"
    title: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    stock: int = Field(default=0, ge=0)

    class Config:
        json_encoders = {ObjectId: str}  # Convertit `_id` en string pour JSON
