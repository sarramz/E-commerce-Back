from fastapi import APIRouter, HTTPException
from typing import List
from config.config import db
from models.product import Product

product_router = APIRouter(prefix="/products", tags=["Produits"])

@product_router.get("/", response_model=List[Product])
async def get_all_products(limit: int = 0, sort: str = "asc"):
    """Récupérer tous les produits avec pagination et tri."""
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find({}, {"_id": 0}).limit(limit).sort("id", sort_order).to_list(length=limit)
    return products

@product_router.get("/{id}", response_model=Product)
async def get_product(id: int):
    """Récupérer un produit par ID."""
    product = await db.products.find_one({"id": id}, {"_id": 0})
    if product:
        return product
    raise HTTPException(status_code=404, detail="Produit non trouvé")

@product_router.get("/categories", response_model=List[str])
async def get_product_categories():
    """Obtenir toutes les catégories uniques de produits."""
    categories = await db.products.distinct("category")
    return categories

@product_router.get("/category/{category}", response_model=List[Product])
async def get_products_in_category(category: str, limit: int = 0, sort: str = "asc"):
    """Récupérer tous les produits d'une catégorie spécifique."""
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find({"category": category}, {"_id": 0}).limit(limit).sort("id", sort_order).to_list(length=limit)
    return products

@product_router.post("/", response_model=Product)
async def add_product(product: Product):
    """Ajouter un nouveau produit."""
    existing_product = await db.products.find_one({"id": product.id})
    if existing_product:
        raise HTTPException(status_code=400, detail="L'ID du produit existe déjà")

    await db.products.insert_one(product.dict())
    return product

@product_router.put("/{id}", response_model=Product)
async def edit_product(id: int, product: Product):
    """Modifier un produit existant."""
    updated_product = await db.products.find_one_and_update(
        {"id": id}, {"$set": product.dict()}, return_document=True
    )
    if updated_product:
        return updated_product
    raise HTTPException(status_code=404, detail="Produit non trouvé")

@product_router.delete("/{id}")
async def delete_product(id: int):
    """Supprimer un produit."""
    deleted_product = await db.products.find_one_and_delete({"id": id})
    if deleted_product:
        return {"message": "Produit supprimé avec succès"}
    raise HTTPException(status_code=404, detail="Produit non trouvé")
