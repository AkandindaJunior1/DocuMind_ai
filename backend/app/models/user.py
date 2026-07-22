import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import the Base blueprint we created in database.py
from ..database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to users (1 organization has many users)
    users = relationship("User", back_populates="organization")
    
    # Relationship to documents (1 organization has many documents)
    documents = relationship("Document", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # Foreign key linking this user to an organization
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    
    role = Column(Enum(RoleEnum), default=RoleEnum.MEMBER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to organization
    organization = relationship("Organization", back_populates="users")
    
    # Relationship to conversations (1 user has many conversations)
    conversations = relationship("Conversation", back_populates="user")
