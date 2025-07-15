from dotenv import load_dotenv
load_dotenv()  # Charger les variables d’environnement tôt

import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Setup JWT secret
SECRET = os.getenv("JWT_SECRET")
if not SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set")

# Auth schema: Bearer Token seulement
oauth2_scheme = HTTPBearer()

# Hashing utils
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Générer un JWT token
def create_token(user_data: dict, expires: timedelta = timedelta(hours=2)) -> str:
    payload = {
        "sub": user_data["email"],
        "role": user_data.get("role", "user"),
        "exp": datetime.utcnow() + expires,
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

# Extraire l'utilisateur à partir du token Bearer
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

# Protection pour routes admin
async def admin_required(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
