import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# 1. Setup Password Hashing
# We use bcrypt. "deprecated=auto" means if a better algorithm comes out later, 
# passlib will automatically upgrade passwords when users log in.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Setup JWT (Digital ID Cards)
# The SECRET_KEY is the master cryptographic key. If a hacker gets this, 
# they can forge ID cards for any user. Never commit this to GitHub!
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Tokens last for 7 days

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the typed password matches the saved hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Turns a plain text password into a secure bcrypt hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates the JWT (The Digital ID Card)"""
    to_encode = data.copy()
    
    # Set the expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Cryptographically sign the token using our SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
