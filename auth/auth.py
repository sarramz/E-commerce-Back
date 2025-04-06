from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#Hashage et vérification de mot de passe
def hash_password(password: str) -> str:
    """Hashage sécurisé du mot de passe."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)
