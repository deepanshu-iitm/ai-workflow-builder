from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, default="Untitled Workflow")
    description = Column(Text, nullable=True)
    
    # Workflow configuration
    is_valid = Column(Boolean, default=False)
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workflow {self.name}>"


class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    
    # Node info
    node_id = Column(String(100), nullable=False)  # React Flow node ID
    node_type = Column(String(50), nullable=False)  # input, knowledgebase, llm, output
    label = Column(String(255), nullable=True)
    
    # Position
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    
    # Configuration stored as JSON
    config = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="nodes")
    
    def __repr__(self):
        return f"<WorkflowNode {self.node_type}:{self.node_id}>"


class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    
    # Edge info
    edge_id = Column(String(100), nullable=False)  # React Flow edge ID
    source_node_id = Column(String(100), nullable=False)
    target_node_id = Column(String(100), nullable=False)
    source_handle = Column(String(50), nullable=True)
    target_handle = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="edges")
    
    def __repr__(self):
        return f"<WorkflowEdge {self.source_node_id} -> {self.target_node_id}>"
