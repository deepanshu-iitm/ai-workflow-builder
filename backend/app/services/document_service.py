import os
import uuid
import fitz  
from typing import List, Tuple, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.core.config import settings


class DocumentService:
    """Service for handling document upload, extraction, and processing."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def upload_document(self, file: UploadFile) -> Document:
        """Upload and save a document to the filesystem."""
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type,
            status="pending"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def extract_text_from_pdf(self, document: Document) -> Tuple[str, int]:
        """Extract text from a PDF document using PyMuPDF."""
        try:
            doc = fitz.open(document.file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            page_count = len(doc)
            
            doc.close()
            
            return full_text, page_count
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def process_document(self, document_id: str) -> Document:
        """Process a document: extract text and update status."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        try:
            document.status = "processing"
            self.db.commit()
            
            # Extract text based on file type
            if document.mime_type == "application/pdf" or document.file_path.endswith(".pdf"):
                content, page_count = self.extract_text_from_pdf(document)
                document.content = content
                document.page_count = page_count
            else:
                # For other file types, try to read as text
                with open(document.file_path, "r", encoding="utf-8") as f:
                    document.content = f.read()
                document.page_count = 1
            
            document.status = "completed"
            self.db.commit()
            self.db.refresh(document)
            
            return document
            
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            self.db.commit()
            raise
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks for embedding."""
        chunks = []
        
        if not text:
            return chunks
        
        # Simple sentence-aware chunking
        sentences = text.replace("\n", " ").split(". ")
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) + 2 <= chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + sentence + ". "
                else:
                    current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents."""
        return self.db.query(Document).order_by(Document.created_at.desc()).all()
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its file."""
        document = self.get_document(document_id)
        
        if not document:
            return False
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete record
        self.db.delete(document)
        self.db.commit()
        
        return True
