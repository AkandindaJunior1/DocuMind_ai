"""
Retrieval-Augmented Generation (RAG) Engine.
Handles searching the vector database and calling the LLM to generate answers.
"""
import os
from google import genai
from sqlalchemy.orm import Session
from typing import List

from ..models.document import DocumentChunk, Document
from .embedder import generate_embeddings

GENERATION_MODEL = "gemini-2.5-flash"

def search_similar_chunks(db: Session, organization_id: str, query: str, limit: int = 5) -> List[DocumentChunk]:
    """
    1. Embeds the user's query.
    2. Searches the vector database for the closest chunks using cosine distance (<=>).
    3. Filters by organization_id so users only search their own company's docs.
    """
    # 1. Embed the query
    # generate_embeddings returns a list of embeddings. We only passed 1 text, so we take the first.
    query_embedding = generate_embeddings([query])[0]
    
    # 2 & 3. Vector search using pgvector's cosine distance operator
    # We join with the Document table to ensure we only search docs belonging to this org.
    results = db.query(DocumentChunk).join(Document).filter(
        Document.organization_id == organization_id,
        Document.status == "completed"
    ).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(limit).all()
    
    return results

def build_rag_prompt(query: str, chunks: List[DocumentChunk], chat_history: List[dict] = None) -> str:
    """
    Constructs the prompt containing the user's question, the retrieved context, and previous chat history.
    """
    if not chunks:
        context_str = "No relevant context documents found in the database."
    else:
        # Build a readable context string from the retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks):
            doc_name = chunk.document.filename
            page = chunk.page_number
            text = chunk.text_content
            context_parts.append(f"--- Document: {doc_name} (Page {page}) ---\n{text}\n")
            
        context_str = "\n".join(context_parts)
        
    # Add chat history
    history_str = ""
    if chat_history and len(chat_history) > 0:
        history_str = "PREVIOUS CONVERSATION HISTORY:\n"
        for msg in chat_history:
            role = "USER" if msg["role"] == "user" else "AI"
            history_str += f"{role}: {msg['content']}\n"
        history_str += "\n"
        
    prompt = f"""You are a helpful AI assistant for a business.
Your goal is to accurately answer the user's question based strictly on the provided context.

RULES:
1. If the answer is not contained in the context, you must clearly state that you don't know based on the provided documents.
2. DO NOT make up information or use outside knowledge to answer specific factual questions.
3. If you use information from the context, briefly mention the document name it came from.
4. You may refer to the PREVIOUS CONVERSATION HISTORY to understand the context of the user's question (e.g. if they say "tell me more about it").

{history_str}CONTEXT:
{context_str}

USER QUESTION:
{query}
"""
    return prompt

def generate_rag_answer_stream(db: Session, organization_id: str, query: str, chat_history: List[dict] = None):
    """
    The full RAG pipeline: Search -> Prompt -> Generate
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
    client = genai.Client(api_key=api_key)
    
    # 1. Search for relevant chunks
    chunks = search_similar_chunks(db, organization_id, query)
    
    # 2. Build the prompt with context
    prompt = build_rag_prompt(query, chunks, chat_history)
    
    # 3. Call Google Gemini to generate the answer via stream
    try:
        response_stream = client.models.generate_content_stream(
            model=GENERATION_MODEL,
            contents=prompt
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        print(f"Error generating RAG answer: {e}")
        yield "I'm sorry, I encountered an error while trying to generate an answer."
