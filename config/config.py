from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis .env
load_dotenv()


MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

SECRET_KEY = os.getenv("SECRET_KEY")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not set in .env file")

client = AsyncIOMotorClient(MONGODB_URL)

db = client.ecommerce
users_collection = db["users"] 


async def connect_to_mongo():
    try:
        await client.admin.command('ping')
        print("Connexion à MongoDB réussie!")
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

async def close_mongo_connection():
    try:
        client.close()
        print("Connexion MongoDB fermée")
    except Exception as e:
        print(f"Erreur lors de la fermeture de la connexion MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la fermeture de la connexion")
    
