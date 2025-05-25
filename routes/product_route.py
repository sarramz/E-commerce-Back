from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
from config.config import db
from models.product import Product
from serializers.product_serializer import product_serializer, products_serializer
from auth.jwt_handler import get_current_user
import os
import shutil

product_router = APIRouter(prefix="", tags=["Produits"])

def is_valid_objectid(id: str) -> bool:
    return ObjectId.is_valid(id)

# Dossier pour stocker les images uploadées
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@product_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Fichier non image")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"http://localhost:8000/uploads/{file.filename}"
    return {"url": url}

@product_router.get("/", response_model=List[Product])
async def get_all_products(limit: int = 10, sort: str = "asc"):
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find(
        {}, 
        {"_id": 1, "title": 1, "price": 1, "description": 1, "image": 1, "category": 1, "stock": 1}
    ).limit(limit).sort("title", sort_order).to_list(length=limit)
    return products_serializer(products)

@product_router.get("/{id}", response_model=Product)
async def get_product(id: str):
    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    product = await db.products.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product_serializer(product)

@product_router.get("/category/{category}", response_model=List[Product])
async def get_products_in_category(category: str, limit: int = 10, sort: str = "asc"):
    sort_order = 1 if sort == "asc" else -1
    products = await db.products.find({"category": category}).limit(limit).sort("title", sort_order).to_list(length=limit)
    return products_serializer(products)

@product_router.post("/", response_model=Product)
async def add_product(product: Product, user: dict = Depends(get_current_user)):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    existing_product = await db.products.find_one({"title": product.title})
    if existing_product:
        raise HTTPException(status_code=400, detail="Un produit avec ce titre existe déjà.")

    inserted = await db.products.insert_one(product.dict(exclude={"id"}))
    created_product = await db.products.find_one({"_id": inserted.inserted_id})
    return product_serializer(created_product)

@product_router.put("/{id}", response_model=Product)
async def edit_product(id: str, product: Product, user: dict = Depends(get_current_user)):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    update_data = {k: v for k, v in product.dict(exclude_unset=True).items()}

    updated_product = await db.products.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not updated_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product_serializer(updated_product)

@product_router.delete("/{id}")
async def delete_product(id: str, user: dict = Depends(get_current_user)):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")

    if not is_valid_objectid(id):
        raise HTTPException(status_code=400, detail="ID invalide")

    deleted_product = await db.products.find_one_and_delete({"_id": ObjectId(id)})
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return {"message": "Produit supprimé avec succès"}
