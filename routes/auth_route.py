from fastapi import APIRouter, HTTPException, status
from auth.auth import verify_password, hash_password
from auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from config.config import users_collection
from models.user import User, UserLogin
from datetime import timedelta

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register")
async def register(user: User):
    """
    Inscription d'un utilisateur.
    Vérifie si l'email est déjà utilisé, puis enregistre un nouvel utilisateur avec mot de passe hashé.
    """
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    hashed_password = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "role": "admin" if user.is_admin else "client"
    }
    
    await users_collection.insert_one(new_user)
    return {"message": "Utilisateur créé avec succès"}

@auth_router.post("/login")
async def login(user_login: UserLogin):
    """
    Connexion d'un utilisateur.
    Vérifie l'email et le mot de passe, puis génère un token JWT.
    """
    user = await users_collection.find_one({"email": user_login.email})
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email incorrect")
    
    if not verify_password(user_login.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe incorrect")
    
    # Construction correcte du payload JWT
    token_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "client")
    }
    access_token = create_access_token(
        data=token_data, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "client")
        }
    }
