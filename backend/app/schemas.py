from pydantic import BaseModel, EmailStr
from uuid import UUID

# 1. Incoming Data Schema for Registration
# When React sends data to /register, Pydantic will verify it looks exactly like this.
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    organization_name: str
    full_name: str | None = None

# 2. Outgoing Data Schema for Tokens
# This is what we send back when someone logs in successfully
class Token(BaseModel):
    access_token: str
    token_type: str

# 3. Outgoing Data Schema for User Profiles
# Notice there is NO password field here. This ensures we never accidentally
# send hashed passwords back to the frontend!
class UserResponse(BaseModel):
    id: UUID
    email: str
    organization_id: UUID
    role: str

    class Config:
        from_attributes = True
