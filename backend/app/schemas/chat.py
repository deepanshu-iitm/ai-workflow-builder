from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    extra_data: Dict[str, Any] = {}


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    execution_time_ms: Optional[int]
    tokens_used: Optional[int]
    model_used: Optional[str]
    extra_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    workflow_id: Optional[str] = None
    title: str = "New Chat"


class ChatSessionResponse(BaseModel):
    id: str
    workflow_id: Optional[str]
    title: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatQueryRequest(BaseModel):
    query: str
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Inline workflow definition (if not using saved workflow)
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None


class ChatQueryResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    execution_time_ms: int
    tokens_used: Optional[int]
    model_used: Optional[str]
    sources: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
