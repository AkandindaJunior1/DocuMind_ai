import pytest
from app.services.chunker import chunk_text

def test_chunk_text_basic():
    """Test that text is chunked into appropriate sizes with overlap."""
    text = "A" * 2000
    pages = [{"page": 1, "text": text}]
    
    # Chunk size 1000, overlap 200
    chunks = chunk_text(pages, chunk_size=1000, overlap=200)
    
    assert len(chunks) == 3
    assert chunks[0]["page"] == 1
    
    # First chunk should be exactly 1000 chars
    assert len(chunks[0]["text"]) == 1000
    
    # Second chunk should be 1000 chars (overlapping by 200)
    assert len(chunks[1]["text"]) == 1000
    
    # Check overlap
    assert chunks[0]["text"][-200:] == chunks[1]["text"][:200]
    
def test_chunk_text_multiple_pages():
    """Test that chunker handles multiple pages correctly."""
    pages = [
        {"page": 1, "text": "A" * 500},
        {"page": 2, "text": "B" * 600}
    ]
    
    # Chunk size 1000, overlap 200
    chunks = chunk_text(pages, chunk_size=1000, overlap=200)
    
    # Since total text is 1100, we should get 2 chunks.
    # Chunk 1: "A"*500 + "B"*500
    # Chunk 2: overlap (200 of B) + remaining B (100) -> 300 chars
    
    assert len(chunks) == 2
    assert chunks[0]["text"] == ("A" * 500) + ("B" * 500)
    assert len(chunks[1]["text"]) == 300
    assert chunks[1]["text"] == "B" * 300
    
    # The first chunk spans pages 1 and 2, but we assign the page of the first char
    assert chunks[0]["page"] == 1
    assert chunks[1]["page"] == 2
