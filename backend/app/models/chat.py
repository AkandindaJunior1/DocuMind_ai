import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

# We use an Enum to make sure a message is strictly one of these three types
class MessageRoleEnum(str, enum.Enum):
    USER = "user"     # The human asking a question
    AI = "ai"         # The LLM answering
    SYSTEM = "system" # Internal instructions (e.g., "You are a helpful assistant")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The user who started this conversation
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship back to User
    user = relationship("User", back_populates="conversations")
    
    # Relationship to Messages
    # cascade="all, delete-orphan" means if we delete a conversation, we delete all its messages too.
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The conversation this message belongs to
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    # Who said it?
    role = Column(Enum(MessageRoleEnum), nullable=False)
    
    # What did they say?
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to Conversation
    conversation = relationship("Conversation", back_populates="messages")
