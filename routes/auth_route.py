from fastapi import APIRouter, HTTPException, status
from auth.auth import verify_password, hash_password
from auth.jwt_handler import create_access_token
from config.config import users_collection
from models.user import User, UserLogin
from datetime import timedelta
from passlib.context import CryptContext

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Inscription d'un utilisateur
@auth_router.post("/register")
async def register(user: User):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = {"name": user.name, "email": user.email, "password": hashed_password, "is_admin": user.is_admin}
    
    await users_collection.insert_one(new_user)
    return {"message": "User created successfully"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@auth_router.post("/login")
async def login(user_login: UserLogin):
    """Connexion d'un utilisateur."""
    user = await users_collection.find_one({"email": user_login.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email incorrect",
        )
    
    if not verify_password(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
        )
    
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}