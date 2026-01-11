from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.db.session import get_db
from app.models.workflow import Workflow
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatQueryRequest,
    ChatQueryResponse
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    # Verify workflow exists if provided
    if session_data.workflow_id:
        workflow = db.query(Workflow).filter(Workflow.id == session_data.workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
    
    session = ChatSession(
        workflow_id=session_data.workflow_id,
        title=session_data.title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    workflow_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all chat sessions."""
    query = db.query(ChatSession)
    
    if workflow_id:
        query = query.filter(ChatSession.workflow_id == workflow_id)
    
    sessions = query.order_by(ChatSession.created_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific chat session with messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}


@router.post("/query", response_model=ChatQueryResponse)
async def execute_query(
    request: ChatQueryRequest,
    db: Session = Depends(get_db)
):
    """Execute a query through a workflow and return the response."""
    start_time = time.time()
    
    # Get or create session
    session = None
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    
    if not session:
        session = ChatSession(
            workflow_id=request.workflow_id,
            title=request.query[:50] + "..." if len(request.query) > 50 else request.query
        )
        db.add(session)
        db.flush()
    
    # Get workflow nodes and edges
    nodes = []
    edges = []
    
    if request.workflow_id:
        # Use saved workflow
        workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        nodes = [
            {
                "id": n.node_id,
                "type": n.node_type,
                "config": n.config,
                "data": {"config": n.config}
            }
            for n in workflow.nodes
        ]
        
        edges = [
            {
                "source": e.source_node_id,
                "target": e.target_node_id
            }
            for e in workflow.edges
        ]
    elif request.nodes and request.edges:
        # Use inline workflow definition
        nodes = request.nodes
        edges = request.edges
    else:
        raise HTTPException(
            status_code=400,
            detail="Either workflow_id or nodes/edges must be provided"
        )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    db.flush()
    
    # Execute workflow
    engine = WorkflowEngine(db)
    result = await engine.execute(request.query, nodes, edges)
    
    execution_time = int((time.time() - start_time) * 1000)
    
    # Save assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["response"],
        execution_time_ms=execution_time,
        tokens_used=result.get("tokens_used"),
        model_used=result.get("model_used"),
        extra_data={
            "sources": result.get("sources", []),
            "logs": result.get("logs", [])
        }
    )
    db.add(assistant_message)
    db.commit()
    
    return ChatQueryResponse(
        response=result["response"],
        session_id=session.id,
        message_id=assistant_message.id,
        execution_time_ms=execution_time,
        tokens_used=result.get("tokens_used"),
        model_used=result.get("model_used"),
        sources=result.get("sources", []),
        metadata={
            "logs": result.get("logs", []),
            "success": result.get("success", True)
        }
    )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get all messages for a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages
