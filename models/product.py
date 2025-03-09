from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
