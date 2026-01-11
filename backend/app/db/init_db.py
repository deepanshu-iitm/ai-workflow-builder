from app.db.base import Base
from app.db.session import engine

from app.models.document import Document
from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge
from app.models.chat import ChatSession, ChatMessage


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
