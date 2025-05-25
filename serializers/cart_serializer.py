def cart_serializer(cart) -> dict:
    return {
        "id": str(cart.get("_id")) if cart.get("_id") else None,
        "userId": str(cart.get("user_id")) if cart.get("user_id") else None,
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

def carts_serializer(carts) -> list:
    return [cart_serializer(cart) for cart in carts]
