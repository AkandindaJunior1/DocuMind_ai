"""
Text chunking service.
Splits extracted document text into smaller, overlapping chunks suitable for vector embeddings.
"""
from typing import List

def chunk_text(pages: List[dict], chunk_size: int = 1000, overlap: int = 200) -> List[dict]:
    """
    Takes a list of pages [{"page": 1, "text": "..."}] and splits them into smaller chunks.
    Returns a list of chunk dicts: [{"page": 1, "text": "...", "chunk_index": 0}, ...]
    
    Uses a sliding window approach with character count.
    """
    chunks = []
    
    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]
        
        # If the page text is empty, skip
        if not text:
            continue
            
        # If the entire page is smaller than the chunk size, it's just one chunk
        if len(text) <= chunk_size:
            chunks.append({
                "page": page_num,
                "text": text,
                "chunk_index": 0
            })
            continue
            
        # Sliding window chunking
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # The end of our current window
            end = start + chunk_size
            
            # If we're not at the very end of the text, try to find a natural break (newline or space)
            # We look backwards from the 'end' index to find the last space/newline within the overlap zone
            if end < len(text):
                # Search window for a natural break: from (end - overlap) to end
                search_start = max(start, end - overlap)
                
                # First try to break on a double newline (paragraph)
                break_point = text.rfind('\n\n', search_start, end)
                
                # If no paragraph break, try a single newline
                if break_point == -1:
                    break_point = text.rfind('\n', search_start, end)
                    
                # If no newline, try a space
                if break_point == -1:
                    break_point = text.rfind(' ', search_start, end)
                
                # If we found a natural break, adjust the end to that point
                if break_point != -1:
                    end = break_point + 1 # Include the break character
            
            # Extract the chunk text
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "page": page_num,
                    "text": chunk_text,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
                
            # Move the start forward, subtracting the overlap from the current end
            # This ensures the next chunk starts slightly before the end of this chunk
            start = end - overlap
            
            # Prevent infinite loops if overlap >= chunk size or no progress is made
            if start <= 0 or end - start <= 0:
                break
                
    return chunks
