import os
import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default ChromaDB settings
DEFAULT_COLLECTION = "content_library"
DB_DIRECTORY = "chroma_db"

class VectorDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDBClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the ChromaDB client."""
        try:
            # Make sure the DB directory exists
            os.makedirs(DB_DIRECTORY, exist_ok=True)
            
            # Create the client
            self.client = chromadb.PersistentClient(
                path=DB_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            # Get or create the default collection
            try:
                self.collection = self.client.get_collection(DEFAULT_COLLECTION)
                logger.info(f"Using existing collection: {DEFAULT_COLLECTION}")
            except ValueError:
                self.collection = self.client.create_collection(
                    name=DEFAULT_COLLECTION,
                    metadata={"description": "Content library for the content writer agent"}
                )
                logger.info(f"Created new collection: {DEFAULT_COLLECTION}")
                
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the vector database.
        
        Args:
            query_text: The query text
            n_results: Maximum number of results to return
            
        Returns:
            results: A list of query results
        """
        try:
            # Query the collection
            raw_results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format the results
            results = []
            
            # Check if we have any results
            if raw_results["documents"] and len(raw_results["documents"]) > 0:
                documents = raw_results["documents"][0]  # Get the documents for the first (and only) query
                metadatas = raw_results["metadatas"][0]  # Get the metadata for the first (and only) query
                
                for i, doc in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    
                    results.append({
                        "title": metadata.get("title", "Untitled Document"),
                        "body": doc,
                        "source": "vector_db",
                        "metadata": metadata
                    })
            
            logger.info(f"Found {len(results)} results in vector DB")
            
            return results
        except Exception as e:
            logger.error(f"Error querying vector DB: {str(e)}")
            # Return an empty list if there's an error
            return []
    
    def add_document(
        self, 
        document: str, 
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """Add a document to the vector database.
        
        Args:
            document: The document text
            metadata: Metadata for the document
            document_id: Optional ID for the document
            
        Returns:
            id: The ID of the added document
        """
        try:
            # Generate a document ID if not provided
            if document_id is None:
                import uuid
                document_id = str(uuid.uuid4())
            
            # Add the document
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[document_id]
            )
            
            logger.info(f"Added document with ID: {document_id}")
            
            return document_id
        except Exception as e:
            logger.error(f"Error adding document to vector DB: {str(e)}")
            raise

def query_vector_db(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Query the vector database for relevant documents.
    
    Args:
        query: The query text
        n_results: Maximum number of results to return
        
    Returns:
        results: A list of query results
    """
    try:
        # Get the vector DB client
        client = VectorDBClient()
        
        # Query the vector DB
        results = client.query(query, n_results=n_results)
        
        return results
    except Exception as e:
        logger.error(f"Error in query_vector_db: {str(e)}")
        # Return an empty list if there's an error
        return []