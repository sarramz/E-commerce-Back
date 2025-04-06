from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
from config.config import db
from models.product import Product
from serializers.product_serializer import product_serializer, products_serializer
from auth.jwt_handler import get_current_user

product_router = APIRouter(prefix="/products", tags=["Produits"])

# Vérification si un ID est valide
def is_valid_objectid(id: str) -> bool:
    return ObjectId.is_valid(id)

# Récupérer tous les produits
@product_router.get("/", response_model=List[Product])
async def get_all_products(limit: int = 10, sort: str = "asc"):
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find({}, {"_id": 1, "title": 1, "price": 1, "description": 1, "image": 1, "category": 1, "stock": 1}) \
                               .limit(limit) \
                               .sort("title", sort_order) \
                               .to_list(length=limit)
    return products_serializer(products)


#  Récupérer un produit par ID
@product_router.get("/{id}", response_model=Product)
async def get_product(id: str):
    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    product = await db.products.find_one({"_id": ObjectId(id)})
    if product:
        return product_serializer(product)
    raise HTTPException(status_code=404, detail="Produit non trouvé")

# Récupérer les produits d'une catégorie
@product_router.get("/category/{category}", response_model=List[Product])
async def get_products_in_category(category: str, limit: int = 10, sort: str = "asc"):
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find({"category": category}).limit(limit).sort("title", sort_order).to_list(length=limit)
    return products_serializer(products)

# Ajouter un produit (ADMIN uniquement)
@product_router.post("/", response_model=Product)
async def add_product(product: Product, user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    existing_product = await db.products.find_one({"title": product.title})
    if existing_product:
        raise HTTPException(status_code=400, detail="Un produit avec ce titre existe déjà.")

    new_product = await db.products.insert_one(product.dict(exclude={"id"}))
    created_product = await db.products.find_one({"_id": new_product.inserted_id})

    return product_serializer(created_product)


#  Modifier un produit (ADMIN uniquement)
@product_router.put("/{id}", response_model=Product)
async def edit_product(id: str, product: Product, user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    update_data = {k: v for k, v in product.dict(exclude_unset=True).items()}  # Exclure les champs non fournis

    updated_product = await db.products.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_product:
        return product_serializer(updated_product)
    raise HTTPException(status_code=404, detail="Produit non trouvé")

#  Supprimer un produit (ADMIN uniquement)
@product_router.delete("/{id}")
async def delete_product(id: str, user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    deleted_product = await db.products.find_one_and_delete({"_id": ObjectId(id)})
    if deleted_product:
        return {"message": "Produit supprimé avec succès"}
    raise HTTPException(status_code=404, detail="Produit non trouvé")


