from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import verify_password, hash_password
from auth.jwt_handler import create_access_token
from config.config import users_collection
from models.user import User
from datetime import timedelta

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

# Connexion + JWT Token
@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": user["email"]}, expires_delta=timedelta(hours=2))
    return {"access_token": access_token, "token_type": "bearer"}
