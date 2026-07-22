"""
Embedding service.
Uses Google Gemini to convert text chunks into mathematical vectors (embeddings).
"""
import os
from google import genai
from typing import List

# The recommended model for text embeddings
EMBEDDING_MODEL = "gemini-embedding-2"

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Takes a list of string texts and returns a list of embedding vectors (list of floats).
    Uses the new google-genai SDK.
    """
    if not texts:
        return []
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Cannot generate embeddings.")
        
    client = genai.Client(api_key=api_key)
    
    try:
        all_embeddings = []
        batch_size = 50
        
        # Google Gemini API only allows 100 items per batch request
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch_texts
            )
            
            # Extract the embeddings from the response
            batch_embeddings = [emb.values for emb in result.embeddings]
            all_embeddings.extend(batch_embeddings)
            
        return all_embeddings
        
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise
