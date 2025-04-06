def user_serializer(user) -> dict:
    """Sérialisation sécurisée de l'utilisateur."""
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False)
    }
