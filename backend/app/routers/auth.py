from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, Organization
from ..schemas import UserCreate, Token, UserResponse
from ..auth import get_password_hash, verify_password, create_access_token
from ..dependencies import get_current_user

# This creates a mini-FastAPI app just for Authentication
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new Organization and its first User (Admin)"""
    
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # 2. Create the Organization
    org = Organization(name=user_data.organization_name)
    db.add(org)
    db.commit()
    db.refresh(org) # This loads the newly generated UUID from the database
    
    # 3. Create the User, hashing the password before saving
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        organization_id=org.id,
        role="admin" # The first user is always the admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs the user in and returns a JWT Digital ID Card"""
    
    # 1. Find user by email (OAuth2 standard uses 'username' field for the email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Check if user exists AND password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Create digital ID card (JWT) with their email and ID embedded inside
    access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    This endpoint is PROTECTED. 
    If you do not send a valid JWT, the Bouncer (get_current_user) will block you.
    If you do, it returns your profile data.
    """
    return current_user
