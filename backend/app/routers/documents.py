import os
import shutil
import uuid
import traceback
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path

from ..database import get_db
from ..models.user import User
from ..models.document import Document, DocumentChunk
from ..dependencies import get_current_user

# Import our new pipeline services
from ..services.extractor import extract_text
from ..services.chunker import chunk_text
from ..services.embedder import generate_embeddings

router = APIRouter(prefix="/documents", tags=["Documents"])

# Temporary storage for uploaded files before they are processed
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def process_document_pipeline(document_id: str, file_path: str, file_name: str, db: Session):
    """
    This function runs the entire AI pipeline: Extract -> Chunk -> Embed -> Save.
    We can run this in a FastAPI BackgroundTask so the user doesn't have to wait.
    """
    try:
        # Get the file extension (e.g., .pdf, .docx)
        file_ext = file_name.split('.')[-1].lower()
        
        # 1. EXTRACT
        print(f"[{document_id}] Extracting text...")
        pages = extract_text(file_path, file_ext)
        
        # 2. CHUNK
        print(f"[{document_id}] Chunking text...")
        chunks = chunk_text(pages, chunk_size=1000, overlap=200)
        
        if not chunks:
            raise ValueError("No text could be extracted or chunked from the document.")
            
        # 3. EMBED
        print(f"[{document_id}] Generating embeddings for {len(chunks)} chunks...")
        # We extract just the text strings for the embedder
        texts_to_embed = [chunk["text"] for chunk in chunks]
        embeddings = generate_embeddings(texts_to_embed)
        
        # 4. SAVE TO DATABASE
        print(f"[{document_id}] Saving chunks and vectors to database...")
        db_chunks = []
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=document_id,
                page_number=chunk["page"],
                text_content=chunk["text"],
                embedding=embeddings[i]  # The mathematical vector!
            )
            db_chunks.append(db_chunk)
            
        db.add_all(db_chunks)
        
        # Update document status
        document = db.query(Document).filter(Document.id == document_id).first()
        document.status = "completed"
        db.commit()
        
        print(f"[{document_id}] Pipeline complete!")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[{document_id}] Pipeline failed: {e}")
        print(error_trace)
        
        # Write the full error to a file so Antigravity can read it
        with open("pipeline_error.txt", "w") as f:
            f.write(error_trace)
            
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "failed"
            db.commit()
            
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receives a file upload, creates a database record, and kicks off the AI pipeline in the background.
    """
    # Allowed file types
    allowed_extensions = ["pdf", "docx", "txt", "csv", "xlsx"]
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")
        
    # 1. Save the file temporarily to disk
    file_id = str(uuid.uuid4())
    temp_file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Create the Document record in the database with status "processing"
    new_doc = Document(
        id=file_id,
        organization_id=current_user.organization_id,
        filename=file.filename,
        file_type=file_ext,
        status="processing"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # 3. Kick off the heavy AI pipeline in the background
    background_tasks.add_task(
        process_document_pipeline, 
        document_id=new_doc.id, 
        file_path=str(temp_file_path), 
        file_name=file.filename, 
        db=db
    )
    
    return {
        "message": "File uploaded successfully. Processing started.",
        "document_id": new_doc.id,
        "status": new_doc.status
    }

@router.get("/")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all documents belonging to the user's organization.
    """
    documents = db.query(Document).filter(
        Document.organization_id == current_user.organization_id
    ).order_by(Document.created_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "status": doc.status,
            "created_at": doc.created_at
        } for doc in documents
    ]

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a document and all its chunks from the database.
    Verifies that the document belongs to the user's organization.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == current_user.organization_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.delete(document) # This will cascade delete DocumentChunks if set up correctly, but let's be explicit just in case
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    db.commit()
    
    return {"message": "Document deleted successfully"}
