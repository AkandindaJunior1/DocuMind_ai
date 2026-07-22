import os
import sys

# Add the current directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.document import Document, DocumentChunk

def check_database():
    db = SessionLocal()
    try:
        # Check Documents
        docs = db.query(Document).all()
        print(f"\n=== DOCUMENTS FOUND: {len(docs)} ===")
        for doc in docs:
            print(f"- Title: {doc.filename}")
            print(f"  Status: {doc.status}")
            print(f"  Type: {doc.file_type}")
            print(f"  ID: {doc.id}")
            
        # Check Chunks
        chunks = db.query(DocumentChunk).all()
        print(f"\n=== CHUNKS (VECTORS) FOUND: {len(chunks)} ===")
        if chunks:
            sample = chunks[0]
            print(f"Sample Chunk Text:\n'{sample.text_content[:150]}...'")
            print(f"Sample Vector Dimension: {len(sample.embedding) if sample.embedding else 0} (Expected 768 for Gemini)")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
