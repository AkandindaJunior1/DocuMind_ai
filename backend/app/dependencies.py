from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from uuid import UUID

from .database import get_db
from .auth import SECRET_KEY, ALGORITHM
from .models.user import User

# This tells FastAPI to look for the token in the "Authorization" HTTP header.
# The tokenUrl parameter tells the Swagger UI exactly where the login endpoint is,
# so the green "Authorize" button on the docs page works magically.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This is our "Bouncer" function. We attach this to any endpoint we want to protect.
    It reads the JWT, verifies it hasn't been tampered with, and fetches the User from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the digital ID card using our master SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extract the user's ID from the payload
        user_id_str: str = payload.get("user_id")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
        
    except jwt.PyJWTError:
        # If the token is expired or forged, we kick them out
        raise credentials_exception
        
    # 3. Double check the user actually still exists in our database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    # 4. Success! Hand the full User object over to the endpoint
    return user
