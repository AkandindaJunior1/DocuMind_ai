from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.document import Document, DocumentChunk
from ..models.chat import Conversation, Message
from ..dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns statistics for the dashboard.
    Counts are scoped to the user's organization.
    """
    org_id = current_user.organization_id
    
    # 1. Total Documents
    total_docs = db.query(Document).filter(
        Document.organization_id == org_id
    ).count()
    
    # 2. Total Chunks (AI Knowledge)
    total_chunks = db.query(DocumentChunk).join(Document).filter(
        Document.organization_id == org_id
    ).count()
    
    # 3. Total Conversations
    # Conversations belong to the user
    total_convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()
    
    # 4. Total Messages
    total_msgs = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()
    
    return {
        "documents": total_docs,
        "chunks": total_chunks,
        "conversations": total_convs,
        "messages": total_msgs
    }
