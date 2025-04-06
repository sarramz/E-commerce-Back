from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from typing import List, Optional
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo import ReturnDocument
from config.config import db
from models.cart import Cart, CartCreate, CartProduct, ProductToRemove
# from models.product import Product  # Removed as it is not accessed
from serializers.cart_serializer import cart_serializer, carts_serializer
from auth.jwt_handler import decode_jwt, get_current_user

cart_router = APIRouter(prefix="/carts", tags=["Carts"])

# Fonction utilitaire pour convertir une chaîne de date en objet datetime
def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez AAAA-MM-JJ.")
@cart_router.get("/", response_model=List[Cart])
async def get_carts(
    limit: int = Query(10, ge=1, le=100),  # Limite des résultats (entre 1 et 100)
    sort: str = Query("asc", regex="^(asc|desc)$"),  # Ordre de tri (ascendant ou descendant)
    startdate: Optional[str] = Query("1970-01-01"),  # Date de début (par défaut 1970-01-01)
    enddate: Optional[str] = Query(str(datetime.today().date())),  # Date de fin (par défaut aujourd'hui)
    user: dict = Depends(get_current_user)  # Utilisateur actuel (dépend du token JWT)
):
    """
    Récupère tous les paniers dans une plage de dates, triés et limités.
    Accessible uniquement aux administrateurs.
    """
    # Vérification des permissions (admin uniquement)
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Seuls les administrateurs peuvent accéder à tous les paniers.")

    # Conversion des dates en objets datetime
    try:
        start = parse_date(startdate)
        end = parse_date(enddate)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"Erreur de format de date : {e.detail}")

    # Définir l'ordre de tri
    sort_order = 1 if sort == "asc" else -1

    # Recherche des paniers dans la base de données
    try:
        carts = await db.carts.find(
            {"date": {"$gte": start, "$lte": end}},  # Filtrer par plage de dates
        ).limit(limit).sort("date", sort_order).to_list(length=limit)  # Limiter et trier les résultats

        # Sérialiser les paniers
        serialized_carts = carts_serializer(carts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des paniers : {str(e)}")

    return serialized_carts

# Route pour ajouter un panier
# @cart_router.post("/cart", response_model=Cart)
# async def create_cart(cart: CartCreate, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     user_data = decode_jwt(token.credentials)
#     user_id = user_data["id"]

#     total_price = 0
#     valid_items = []

#     for item in cart.products:
#         # Vérification que l'ID est un ObjectId valide
#         if not ObjectId.is_valid(item.productId):
#             raise HTTPException(status_code=400, detail=f"ID produit invalide : {item.productId}")

#         # Récupération du produit
#         try:
#             product = await db.products.find_one({"_id": ObjectId(item.productId)})
#         except Exception:
#             raise HTTPException(status_code=400, detail=f"ID produit invalide ou mal formaté : {item.productId}")

#         if not product:
#             raise HTTPException(status_code=404, detail=f"Produit non trouvé : {item.productId}")
     
#         # Vérifie si la quantité est disponible
#         if "stock" not in product or item.quantity > product["stock"]:
#             raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {product['title']}")

#         # Calcul du prix total
#         total_price += product["price"] * item.quantity

#         valid_items.append(item.model_dump())

#     # Structure du panier à insérer
#     cart_data = {
#         "user_id": user_id,
#         "products": valid_items,
#         "total_price": total_price,
#         "date": datetime.now(timezone.utc)  # Assurez-vous d'ajouter la date du panier
#     }

#     # Insertion en base
#     result = await db.carts.insert_one(cart_data)
#     new_cart = await db.carts.find_one({"_id": result.inserted_id})
#     # print("DEBUG new_cart:", new_cart)  # Debugging pour voir le contenu du panier créé
#     #je veux voir lid du new cart 
#     print(f"DEBUG: New cart ID is {new_cart['_id']}")  # Afficher l'ID du nouveau panier
#     # Conversion _id en string pour la réponse
#     new_cart["id"] = str(new_cart.pop("_id"))  # Ensure _id is mapped to id
#     new_cart["userId"] = str(new_cart.pop("user_id"))  # Map user_id to userId as a string
#     print("DEBUG new_cart after mapping:", new_cart)  # Debugging pour voir le panier après le mapping
#     return cart_serializer(new_cart)
@cart_router.post("/cart", response_model=Cart)
async def create_cart(cart: CartCreate, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    user_data = decode_jwt(token.credentials)
    user_id = user_data["id"]

    total_price = 0
    valid_items = []

    for item in cart.products:
        if not ObjectId.is_valid(item.productId):
            raise HTTPException(status_code=400, detail=f"ID produit invalide : {item.productId}")

        product = await db.products.find_one({"_id": ObjectId(item.productId)})

        if not product:
            raise HTTPException(status_code=404, detail=f"Produit non trouvé : {item.productId}")

        if "stock" not in product or item.quantity > product["stock"]:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {product['title']}")

        total_price += product["price"] * item.quantity
        valid_items.append(item.model_dump())

    cart_data = {
        "user_id": ObjectId(user_id),
        "products": valid_items,
        "total_price": total_price,
        "date": datetime.now(timezone.utc)
    }

    result = await db.carts.insert_one(cart_data)
    new_cart = await db.carts.find_one({"_id": result.inserted_id})

    # Mapping pour correspondre au modèle Cart
    return Cart(
        id=str(new_cart["_id"]),
        userId=str(new_cart["user_id"]),
        products=new_cart["products"],
        total_price=new_cart["total_price"],
        date=new_cart["date"]
    )
    
# Route pour modifier un panier
from datetime import datetime, timezone
from models.cart import Cart, CartCreate

@cart_router.put("/{id}", response_model=Cart)
async def update_cart(id: str, cart: CartCreate, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de panier invalide")

    existing_cart = await db.carts.find_one({"_id": ObjectId(id)})
    if not existing_cart:
        raise HTTPException(status_code=404, detail="Panier introuvable")

    if not (user.get("is_admin") or str(existing_cart["user_id"]) == str(user["id"])):
        raise HTTPException(status_code=403, detail="Non autorisé à modifier ce panier")

    for product in cart.products:
        if product.quantity < 1:
            raise HTTPException(status_code=400, detail="La quantité doit être au moins 1.")

    update_data = cart.model_dump()

    # On met à jour le panier
    updated_cart = await db.carts.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {
            "products": update_data["products"],
            "date": datetime.now(timezone.utc)
        }},
        return_document=ReturnDocument.AFTER
    )

    # On renvoie le modèle Cart complet
    return Cart(
        id=str(updated_cart["_id"]),
        userId=str(updated_cart["user_id"]),
        products=updated_cart["products"],
        total_price=updated_cart["total_price"],
        date=updated_cart["date"]
    )

# Route pour supprimer un panier
@cart_router.delete("/{id}")
async def delete_cart(id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide.")

    cart = await db.carts.find_one({"_id": ObjectId(id)})
    if not cart:
        raise HTTPException(status_code=404, detail="Panier introuvable.")

    if not (user.get("is_admin") or str(cart["user_id"]) == str(user["id"])):
        raise HTTPException(status_code=403, detail="Accès interdit.")

    await db.carts.delete_one({"_id": ObjectId(id)})
    return {"message": "Panier supprimé avec succès."}

# Vider un panier sans le supprimer
@cart_router.delete("/{id}/clear")
async def clear_cart(id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de panier invalide.")

    cart = await db.carts.find_one({"_id": ObjectId(id)})
    if not cart:
        raise HTTPException(status_code=404, detail="Panier introuvable.")

    if not (user.get("is_admin") or str(cart["user_id"]) == str(user["id"])):
        raise HTTPException(status_code=403, detail="Accès refusé.")

    await db.carts.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "products": [],
            "total_price": 0.0,
            "date": datetime.now(timezone.utc)
        }}
    )

    return {"message": "Panier vidé avec succès."}

# Ajouter un produit ou augmenter la quantité
@cart_router.patch("/{id}/add-product", response_model=Cart)
async def add_product_to_cart(
    id: str,
    product: CartProduct = Body(...),
    user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de panier invalide")

    cart = await db.carts.find_one({"_id": ObjectId(id)})
    if not cart:
        raise HTTPException(status_code=404, detail="Panier introuvable")

    if not (user.get("is_admin") or str(cart["user_id"]) == str(user["id"])):
        raise HTTPException(status_code=403, detail="Non autorisé à modifier ce panier")

    existing_product = next((p for p in cart["products"] if p["productId"] == product.productId), None)
    if existing_product:
        existing_product["quantity"] += product.quantity
    else:
        cart["products"].append(product.model_dump())

    updated_cart = await db.carts.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {
            "products": cart["products"],
            "date": datetime.now(timezone.utc)
        }},
        return_document=ReturnDocument.AFTER
    )

    return Cart(
        id=str(updated_cart["_id"]),
        userId=str(updated_cart["user_id"]),
        products=updated_cart["products"],
        total_price=updated_cart["total_price"],
        date=updated_cart["date"]
    )

# Supprimer un produit d’un panier

@cart_router.patch("/{id}/remove-product", response_model=Cart)
async def remove_product_from_cart(
    id: str,
    body: ProductToRemove,
    user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de panier invalide")

    cart = await db.carts.find_one({"_id": ObjectId(id)})
    if not cart:
        raise HTTPException(status_code=404, detail="Panier introuvable")

    if not (user.get("is_admin") or str(cart["user_id"]) == str(user["id"])):
        raise HTTPException(status_code=403, detail="Non autorisé à modifier ce panier")

    # Bien utiliser la bonne clé "productId"
    updated_products = [p for p in cart["products"] if p["productId"] != body.product_id]

    updated_cart = await db.carts.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {
            "products": updated_products,
            "date": datetime.now(timezone.utc)
        }},
        return_document=ReturnDocument.AFTER
    )

    return  Cart(
        id=str(updated_cart["_id"]),
        userId=str(updated_cart["user_id"]),
        products=updated_cart["products"],
        total_price=updated_cart["total_price"],
        date=updated_cart["date"]
    )
