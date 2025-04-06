# Fonction de sérialisation d'un panier
def cart_serializer(cart) -> dict:
    print("DEBUG cart:", cart)  # Ajoute ça temporairement
    return {
        "id": str(cart.get("_id")) if cart.get("_id") else None,
        "userId": str(cart.get("userId")) if cart.get("userId") else None,
        "date": cart.get("date"),
        "products": [
            {
                "productId": str(product.get("productId")),
                "quantity": product.get("quantity")
            }
            for product in cart.get("products", [])
        ],
        "total_price": cart.get("total_price", 0.0)
    }


# Fonction de sérialisation de plusieurs paniers
def carts_serializer(carts) -> list:
    return [cart_serializer(cart) for cart in carts]
