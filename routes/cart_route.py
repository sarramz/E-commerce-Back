from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from pymongo import ReturnDocument
from config.config import db
from models.cart import Cart
from serializers.cart_serializer import cart_serializer, carts_serializer

cart_router = APIRouter(prefix="/carts", tags=["Panier"])

@cart_router.get("/", response_model=List[Cart])
async def get_all_carts(limit: int = 0, sort: str = "asc", startdate: str = "1970-01-01", enddate: str = str(datetime.today().date())):
    """Récupérer tous les paniers avec filtres."""
    sort_order = 1 if sort == "asc" else -1
    carts = await db.carts.find(
        {"date": {"$gte": startdate, "$lt": enddate}}, 
        {"_id": 0, "products._id": 0}
    ).limit(limit).sort("id", sort_order).to_list(length=limit)
    return carts_serializer(carts)

@cart_router.get("/{id}", response_model=Cart)
async def get_single_cart(id: int):
    """Récupérer un panier par ID."""
    cart = await db.carts.find_one({"id": id}, {"_id": 0, "products._id": 0})
    if cart:
        return cart_serializer(cart)
    raise HTTPException(status_code=404, detail="Panier non trouvé")

@cart_router.get("/user/{userid}", response_model=List[Cart])
async def get_carts_by_user(userid: int, startdate: str = "1970-01-01", enddate: str = str(datetime.today().date())):
    """Récupérer tous les paniers d'un utilisateur spécifique."""
    carts = await db.carts.find(
        {"userId": userid, "date": {"$gte": startdate, "$lt": enddate}}, 
        {"_id": 0, "products._id": 0}
    ).to_list(None)

    return carts_serializer(carts)  # Correction ici

@cart_router.post("/", response_model=Cart)
async def add_cart(cart: Cart):
    """Ajouter un panier."""
    existing_cart = await db.carts.find_one({"id": cart.id})
    if existing_cart:
        raise HTTPException(status_code=400, detail="L'ID du panier existe déjà")

    cart_dict = cart.dict()
    cart_dict["date"] = cart.date.isoformat()  # Convertir en format string ISO

    await db.carts.insert_one(cart_dict)
    return cart_serializer(cart_dict)

@cart_router.put("/{id}", response_model=Cart)
async def edit_cart(id: int, cart: Cart):
    """Modifier un panier existant."""
    updated_cart = await db.carts.find_one_and_update(
        {"id": id}, {"$set": cart.dict()}, return_document=ReturnDocument.AFTER
    )
    if updated_cart:
        return cart_serializer(updated_cart)
    raise HTTPException(status_code=404, detail="Panier non trouvé")

@cart_router.delete("/{id}")
async def delete_cart(id: int):
    """Supprimer un panier."""
    deleted_cart = await db.carts.find_one_and_delete({"id": id})
    if deleted_cart:
        return {"message": "Panier supprimé avec succès"}
    raise HTTPException(status_code=404, detail="Panier non trouvé")
