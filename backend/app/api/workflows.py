from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowValidationResponse,
    WorkflowExecuteRequest
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter()


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description
    )
    db.add(workflow)
    db.flush()
    
    # Add nodes
    for node_data in workflow_data.nodes:
        node = WorkflowNode(
            workflow_id=workflow.id,
            node_id=node_data.node_id,
            node_type=node_data.node_type,
            label=node_data.label,
            position_x=node_data.position_x,
            position_y=node_data.position_y,
            config=node_data.config
        )
        db.add(node)
    
    # Add edges
    for edge_data in workflow_data.edges:
        edge = WorkflowEdge(
            workflow_id=workflow.id,
            edge_id=edge_data.edge_id,
            source_node_id=edge_data.source_node_id,
            target_node_id=edge_data.target_node_id,
            source_handle=edge_data.source_handle,
            target_handle=edge_data.target_handle
        )
        db.add(edge)
    
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(db: Session = Depends(get_db)):
    """List all workflows."""
    workflows = db.query(Workflow).order_by(Workflow.created_at.desc()).all()
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Get a specific workflow by ID."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update basic fields
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    
    # Update nodes if provided
    if workflow_data.nodes is not None:
        # Delete existing nodes
        db.query(WorkflowNode).filter(WorkflowNode.workflow_id == workflow_id).delete()
        
        # Add new nodes
        for node_data in workflow_data.nodes:
            node = WorkflowNode(
                workflow_id=workflow.id,
                node_id=node_data.node_id,
                node_type=node_data.node_type,
                label=node_data.label,
                position_x=node_data.position_x,
                position_y=node_data.position_y,
                config=node_data.config
            )
            db.add(node)
    
    # Update edges if provided
    if workflow_data.edges is not None:
        # Delete existing edges
        db.query(WorkflowEdge).filter(WorkflowEdge.workflow_id == workflow_id).delete()
        
        # Add new edges
        for edge_data in workflow_data.edges:
            edge = WorkflowEdge(
                workflow_id=workflow.id,
                edge_id=edge_data.edge_id,
                source_node_id=edge_data.source_node_id,
                target_node_id=edge_data.target_node_id,
                source_handle=edge_data.source_handle,
                target_handle=edge_data.target_handle
            )
            db.add(edge)
    
    workflow.is_valid = False
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted successfully"}


@router.post("/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Validate a workflow configuration without saving it."""
    engine = WorkflowEngine(db)
    
    # Convert to format expected by engine
    nodes = [
        {
            "id": n.node_id,
            "type": n.node_type,
            "config": n.config
        }
        for n in workflow_data.nodes
    ]
    
    edges = [
        {
            "source": e.source_node_id,
            "target": e.target_node_id
        }
        for e in workflow_data.edges
    ]
    
    result = engine.validate_workflow(nodes, edges)
    
    return WorkflowValidationResponse(
        is_valid=result["is_valid"],
        errors=result["errors"],
        warnings=result["warnings"]
    )


@router.post("/{workflow_id}/validate", response_model=WorkflowValidationResponse)
async def validate_saved_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Validate a saved workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    engine = WorkflowEngine(db)
    
    nodes = [
        {
            "id": n.node_id,
            "type": n.node_type,
            "config": n.config
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
    
    result = engine.validate_workflow(nodes, edges)
    
    # Update workflow validation status
    workflow.is_valid = result["is_valid"]
    workflow.last_validated_at = datetime.utcnow()
    db.commit()
    
    return WorkflowValidationResponse(
        is_valid=result["is_valid"],
        errors=result["errors"],
        warnings=result["warnings"]
    )
