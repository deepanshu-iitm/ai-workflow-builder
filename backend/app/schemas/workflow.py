from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkflowNodeCreate(BaseModel):
    node_id: str
    node_type: str
    label: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    config: Dict[str, Any] = {}


class WorkflowNodeResponse(BaseModel):
    id: str
    node_id: str
    node_type: str
    label: Optional[str]
    position_x: int
    position_y: int
    config: Dict[str, Any]
    
    class Config:
        from_attributes = True


class WorkflowEdgeCreate(BaseModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None


class WorkflowEdgeResponse(BaseModel):
    id: str
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_handle: Optional[str]
    target_handle: Optional[str]
    
    class Config:
        from_attributes = True


class WorkflowCreate(BaseModel):
    name: str = "Untitled Workflow"
    description: Optional[str] = None
    nodes: List[WorkflowNodeCreate] = []
    edges: List[WorkflowEdgeCreate] = []


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[WorkflowNodeCreate]] = None
    edges: Optional[List[WorkflowEdgeCreate]] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_valid: bool
    last_validated_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    nodes: List[WorkflowNodeResponse]
    edges: List[WorkflowEdgeResponse]
    
    class Config:
        from_attributes = True


class WorkflowValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class WorkflowExecuteRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
