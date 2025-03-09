from fastapi import APIRouter, HTTPException, Depends
from config.config import users_collection
from serializers.user_serializer import user_serializer
from auth.jwt_handler import get_current_user

user_router = APIRouter(prefix="/users", tags=["Users"])

# Récupérer le profil utilisateur
# @user_router.get("/me")
# async def get_me(current_user: dict = Depends(get_current_user)):
#     user = await users_collection.find_one({"email": current_user["sub"]})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user_serializer(user)

