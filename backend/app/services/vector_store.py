import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import uuid

from app.core.config import settings


class VectorStoreService:
    """Service for managing ChromaDB vector store operations."""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create ChromaDB client (singleton pattern)."""
        if cls._client is None:
            cls._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return cls._client
    
    def __init__(self, collection_name: str = "default"):
        self.client = self.get_client()
        self.collection_name = collection_name
        self._collection = None
    
    @property
    def collection(self):
        """Get or create collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents with embeddings to the collection."""
        if not texts or not embeddings:
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadatas is None:
            metadatas = [{"source": "document"} for _ in texts]
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the collection for similar documents."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        return {
            "documents": results.get("documents", [[]])[0],
            "metadatas": results.get("metadatas", [[]])[0],
            "distances": results.get("distances", [[]])[0],
            "ids": results.get("ids", [[]])[0]
        }
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._collection = None
            return True
        except Exception:
            return False
    
    def delete_documents(self, ids: List[str]):
        """Delete specific documents by ID."""
        if ids:
            self.collection.delete(ids=ids)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        return {
            "name": self.collection_name,
            "count": self.collection.count()
        }
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        collections = self.client.list_collections()
        return [c.name for c in collections]
