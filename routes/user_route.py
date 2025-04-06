from fastapi import APIRouter, HTTPException, Depends
from models.user import User
from config.config import db
from auth.jwt_handler import get_current_user

user_router = APIRouter(prefix="/users", tags=["Utilisateurs"])

# @user_router.post("/", response_model=User)
# async def create_user(user: User, current_user: dict = Depends(get_current_user)):
#     """Créer un nouvel utilisateur - réservé aux administrateurs."""
#     await verify_role(current_user, RoleEnum.admin)  # Seul l'administrateur peut créer des utilisateurs

#     existing_user = await db.users.find_one({"email": user.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email déjà utilisé")

#     user_dict = user.dict(exclude_unset=True)
#     new_user = await db.users.insert_one(user_dict)
#     created_user = await db.users.find_one({"_id": new_user.inserted_id})
#     return User(**created_user)

# @user_router.put("/{user_id}", response_model=User)
# async def update_user_role(user_id: str, user_update: User, current_user: dict = Depends(get_current_user)):
#     """Mettre à jour le rôle d'un utilisateur - réservé aux administrateurs."""
#     await verify_role(current_user, RoleEnum.admin)  # Seul l'administrateur peut mettre à jour un utilisateur

#     updated_user = await db.users.find_one_and_update(
#         {"_id": user_id},
#         {"$set": {"role": user_update.role}},
#         return_document=ReturnDocument.AFTER
#     )
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
#     return User(**updated_user)
