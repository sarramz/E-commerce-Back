def product_serializer(product) -> dict:
    """Transforme un document MongoDB en dict Python pour Product."""
    return {
        "id": str(product["_id"]),
        "title": product["title"],
        "price": product["price"],
        "description": product.get("description", ""),
        "image": product.get("image", ""),
        "category": product.get("category", "")
    }

def products_serializer(products) -> list:
    """Transforme une liste de produits MongoDB en liste Python."""
    return [product_serializer(product) for product in products]
