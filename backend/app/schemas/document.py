from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str]
    status: str
    error_message: Optional[str]
    page_count: Optional[int]
    chunk_count: int
    is_embedded: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
