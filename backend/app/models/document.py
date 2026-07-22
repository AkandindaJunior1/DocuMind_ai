import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from ..database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The organization this document belongs to
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    file_type = Column(String) # e.g., "pdf", "txt"
    status = Column(String, default="processing") # tracking if the AI is done reading it
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to Organization
    organization = relationship("Organization", back_populates="documents")
    
    # Relationship to its chunks (if we delete a Document, we delete its chunks)
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # The document this chunk belongs to
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # The actual text of the paragraph
    text_content = Column(Text, nullable=False)
    
    # The page number (if applicable, useful for citations!)
    page_number = Column(Integer)
    
    # THE AI MAGIC: The vector embedding array
    # We set dimensions=3072 because Google Gemini's new gemini-embedding-2 model outputs 3072 numbers.
    embedding = Column(Vector(3072))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to Document
    document = relationship("Document", back_populates="chunks")
