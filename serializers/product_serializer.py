def product_serializer(product) -> dict:
    """Convertit un document MongoDB en dict Python pour un produit."""
    return {
        "id": str(product["_id"]),
        "title": product.get("title", ""),
        "price": product.get("price", 0.0),
        "description": product.get("description", ""),
        "image": product.get("image", ""),
        "category": product.get("category", ""),
        "stock": product.get("stock", 0)
    }

def products_serializer(products) -> list:
    """Convertit une liste de documents MongoDB en liste de dicts Python."""
    return [product_serializer(product) for product in products]
