from pinecone import Pinecone, ServerlessSpec
from ..config import get_settings
import time
from pydantic import BaseModel
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MBAEssayEmbedding(BaseModel):
    """Represents an MBA essay embedding with its metadata for vector storage."""
    id: str
    values: List[float]
    metadata: dict = {
        "essay": str,
        "prompt": str,
        "school": str,
        "feedback": str
    }

class MBAEssaySearchResult(BaseModel):
    """Represents a search result from the vector database."""
    score: float
    essay: str
    prompt: str
    school: str
    feedback: str

class PineconeService:
    """Service for managing vector embeddings storage and similarity search using Pinecone."""
    
    def __init__(self) -> None:
        """Initialize Pinecone client and ensure index exists."""
        self.settings = get_settings()
        self.pinecone = Pinecone(api_key=self.settings.pinecone_api_key)
        self._initialize_index()
        
    def _initialize_index(self) -> None:
        """Sets up and connects to the Pinecone index."""
        index_name = self.settings.pinecone_index_name
        
        # Create index if it doesn't exist
        if index_name not in self.pinecone.list_indexes().names():
            logger.info(f"Creating new Pinecone index: {index_name}")
            self._create_and_wait_for_index(index_name)
            
        try:
            self.index = self.pinecone.Index(index_name)
            logger.info("PineconeService initialized successfully")
        except Exception as e:
            error_details = {
                "message": str(e),
                "cause": getattr(e, "__cause__", None),
                "code": getattr(getattr(e, "__cause__", None), "code", None)
            }
            logger.error(f"Pinecone initialization error: {error_details}")
            raise

    def _create_and_wait_for_index(self, index_name: str) -> None:
        """Creates a new Pinecone index and waits for it to be ready."""
        self.pinecone.create_index(
            name=index_name,
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        # Poll until index is ready
        while not self.pinecone.describe_index(index_name).status['ready']:
            time.sleep(1)

    def store_essay_embedding(self, embedding: MBAEssayEmbedding) -> None:
        """Stores an essay embedding in Pinecone."""
        if not hasattr(self, 'index'):
            raise Exception("Pinecone index not initialized")
            
        self.index.upsert([{
            "id": embedding.id,
            "values": embedding.values,
            "metadata": embedding.metadata
        }])
        logger.debug(f"Stored embedding with ID: {embedding.id}")
    
    def search_similar_essays(
        self, 
        query_embedding: List[float], 
        school: str,
        top_k: int = 5
    ) -> List[MBAEssaySearchResult]:
        """Finds similar essays for the given school using vector similarity."""
        try:
            results = self.index.query(
                vector=query_embedding,
                filter={"school": school},
                top_k=top_k,
                include_metadata=True
            )

            return [
                MBAEssaySearchResult(
                    score=match.score,
                    essay=match.metadata["essay"],
                    prompt=match.metadata["prompt"],
                    school=match.metadata["school"],
                    feedback=match.metadata["feedback"]
                )
                for match in results.matches
            ]

        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}")
            return []
