from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.document_service import DocumentService
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.models.document import Document

router = APIRouter()


def process_and_embed_document(document_id: str, db: Session):
    """Background task to process document and create embeddings."""
    doc_service = DocumentService(db)
    llm_service = LLMService()
    
    try:
        # Process document
        document = doc_service.process_document(document_id)
        
        if document.content:
            # Chunk the text
            chunks = doc_service.chunk_text(document.content)
            
            if chunks:
                # Generate embeddings
                embeddings = llm_service.generate_embeddings(chunks)
                
                # Store in vector database
                collection_name = f"doc_{document.id}"
                vector_store = VectorStoreService(collection_name)
                
                metadatas = [
                    {
                        "document_id": document.id,
                        "filename": document.original_filename,
                        "chunk_index": i
                    }
                    for i in range(len(chunks))
                ]
                
                vector_store.add_documents(
                    texts=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                
                # Update document record
                document.collection_name = collection_name
                document.chunk_count = len(chunks)
                document.is_embedded = True
                db.commit()
                
    except Exception as e:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "failed"
            document.error_message = str(e)
            db.commit()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document for processing."""
    # Validate file type
    allowed_types = [
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    if file.content_type not in allowed_types and not file.filename.endswith(('.pdf', '.txt', '.md')):
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: PDF, TXT, MD"
        )
    
    doc_service = DocumentService(db)
    document = await doc_service.upload_document(file)
    
    # Process document in background
    background_tasks.add_task(process_and_embed_document, document.id, db)
    
    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    doc_service = DocumentService(db)
    documents = doc_service.get_all_documents()
    
    return DocumentListResponse(
        documents=documents,
        total=len(documents)
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and its embeddings."""
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store if embedded
    if document.collection_name:
        try:
            vector_store = VectorStoreService(document.collection_name)
            vector_store.delete_collection()
        except Exception:
            pass
    
    # Delete document
    doc_service.delete_document(document_id)
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a document to regenerate embeddings."""
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete existing embeddings
    if document.collection_name:
        try:
            vector_store = VectorStoreService(document.collection_name)
            vector_store.delete_collection()
        except Exception:
            pass
    
    # Reset document status
    document.status = "pending"
    document.is_embedded = False
    document.chunk_count = 0
    db.commit()
    
    # Reprocess in background
    background_tasks.add_task(process_and_embed_document, document_id, db)
    
    return {"message": "Document reprocessing started"}
