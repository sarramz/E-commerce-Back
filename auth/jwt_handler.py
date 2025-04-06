from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Clés et paramètres de l'algorithme pour JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Définir la sécurité pour extraire le token
security = HTTPBearer()

# Fonction pour créer un token d'accès
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crée un token d'accès JWT avec données et expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Fonction pour décoder le token et vérifier sa validité
def decode_jwt(token: str):
    try:
        # Décodage du token avec la clé secrète
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")  # Erreur si le token est invalide

# Fonction pour obtenir l'utilisateur actuel à partir du token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt(token)
    
    # Vérifie que les champs requis existent
    if not all(k in payload for k in ("id", "email", "role")):
        raise HTTPException(status_code=401, detail="Token payload invalid")

    return {
        "id": payload["id"],
        "email": payload["email"],
        "role": payload["role"],
        "is_admin": payload["role"] == "admin"
    }