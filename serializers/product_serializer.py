def product_serializer(product) -> dict:
    """Transforme un document MongoDB en dict Python pour Product."""
    return {
        "id": str(product["_id"]),  # Convertit ObjectId en string
        "title": product.get("title", ""),
        "price": product.get("price", 0.0),
        "description": product.get("description", ""),
        "image": product.get("image", ""),
        "category": product.get("category", ""),
        "stock": product.get("stock", 0)  
    }

def products_serializer(products) -> list:
    """Transforme une liste de produits MongoDB en liste Python."""
    return [product_serializer(product) for product in products]
