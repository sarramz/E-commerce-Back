from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional

#  Modèle représentant un produit dans un panier
class CartProduct(BaseModel):
    productId: str  
    quantity: int 

#  Modèle utilisé pour la création d'un panier (POST)
class CartCreate(BaseModel):
    products: List[CartProduct]

# Modèle complet de panier retourné au client
class Cart(BaseModel):
    id: str # Correspond à _id de MongoDB
    userId: Optional[str]  # ID de l'utilisateur (injecté côté serveur)
    date: datetime = Field(default_factory=datetime.utcnow)
    products: List[CartProduct]
    total_price: float = 0.0

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        

class ProductToRemove(BaseModel):
    product_id: str