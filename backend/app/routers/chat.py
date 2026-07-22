from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from ..database import get_db, SessionLocal
from ..models.user import User
from ..models.chat import Conversation, Message, MessageRoleEnum
from ..dependencies import get_current_user
from ..services.rag import generate_rag_answer_stream

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/conversations")
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new conversation thread for the user.
    """
    new_conv = Conversation(
        user_id=current_user.id,
        title="New Conversation"
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    
    return {
        "id": new_conv.id,
        "title": new_conv.title,
        "created_at": new_conv.created_at
    }

@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets all conversation threads for the current user.
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        } for c in conversations
    ]

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets all messages for a specific conversation.
    Verifies that the conversation belongs to the user.
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return [
        {
            "id": m.id,
            "role": m.role.value,
            "content": m.content,
            "created_at": m.created_at
        } for m in messages
    ]

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    payload: dict, # expecting {"content": "User's question"}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    The core chat endpoint.
    1. Saves the user's message.
    2. Runs the RAG pipeline to get the AI's answer.
    3. Saves the AI's message.
    4. Returns the AI's message.
    """
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
        
    # Verify ownership
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # 1. Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role=MessageRoleEnum.USER,
        content=content
    )
    db.add(user_msg)
    
    # Update conversation title if it's the first message
    messages_count = db.query(Message).filter(Message.conversation_id == conversation_id).count()
    if messages_count == 0:
        conv.title = content[:30] + "..." if len(content) > 30 else content
        
    db.commit()
    
    # Get last 5 messages for sliding window memory
    # Note: we do this after saving the user's message so the current message is not in history
    history = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.id != user_msg.id # Exclude the message we just saved
    ).order_by(Message.created_at.desc()).limit(5).all()
    history.reverse() # Chronological order
    
    chat_history = [{"role": m.role.value, "content": m.content} for m in history]
    
    # Extract org_id before generator to avoid DetachedInstanceError
    org_id = str(current_user.organization_id)
    
    def generate():
        ai_full_content = ""
        # 2. Run the RAG pipeline streaming!
        
        # We need a new session since the generator runs lazily during response streaming
        stream_db = SessionLocal()
        try:
            for chunk in generate_rag_answer_stream(stream_db, org_id, content, chat_history):
                ai_full_content += chunk
                yield chunk
                
            # 3. Save AI message to DB when finished
            ai_msg = Message(
                conversation_id=conversation_id,
                role=MessageRoleEnum.AI,
                content=ai_full_content
            )
            stream_db.add(ai_msg)
            stream_db.commit()
        finally:
            stream_db.close()

    # 4. Return StreamingResponse
    return StreamingResponse(generate(), media_type="text/event-stream")
