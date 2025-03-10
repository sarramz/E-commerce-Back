from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class CartProduct(BaseModel):
    productId: int
    quantity: int

class Cart(BaseModel):
    id: int
    userId: int
    date: datetime  
    products: List[CartProduct]
