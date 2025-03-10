def cart_serializer(cart) -> dict:
    """Transforme un document MongoDB en dict Python pour Cart."""
    return {
        "id": cart["id"],
        "userId": cart["userId"],
        "date": cart["date"],  # Déjà sous format ISO
        "products": [
            {"productId": p["productId"], "quantity": p["quantity"]}
            for p in cart.get("products", [])
        ],
    }

def carts_serializer(carts) -> list:
    """Transforme une liste de paniers MongoDB en liste Python."""
    return [cart_serializer(cart) for cart in carts]
