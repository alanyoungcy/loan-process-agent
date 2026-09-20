"""
Vector Store Service - ChromaDB Integration
Handles document storage, embedding, and retrieval
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store client for ChromaDB
    Manages collections and document operations
    """

    def __init__(self):
        """Initialize ChromaDB client"""
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST,
                port=settings.CHROMADB_PORT,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(
                f"Connected to ChromaDB at {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            raise

    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create a new collection

        Args:
            name: Collection name
            metadata: Optional metadata for the collection

        Returns:
            Collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {"hnsw:space": "cosine"}
            )
            logger.info(f"Created/retrieved collection: {name}")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection {name}: {str(e)}")
            raise

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to a collection

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dicts (must match documents length)
            ids: List of unique IDs (must match documents length)
        """
        try:
            collection = self.client.get_collection(collection_name)

            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(
                f"Added {len(documents)} documents to collection {collection_name}"
            )
        except Exception as e:
            logger.error(
                f"Error adding documents to {collection_name}: {str(e)}"
            )
            raise

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a collection for similar documents

        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return per query
            where: Optional metadata filter
            where_document: Optional document content filter

        Returns:
            Query results dict with ids, documents, metadatas, distances
        """
        try:
            collection = self.client.get_collection(collection_name)

            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document
            )

            logger.info(
                f"Queried {collection_name} with {len(query_texts)} queries, "
                f"returned {len(results['ids'][0])} results"
            )

            return results
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {str(e)}")
            raise

    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Update documents in a collection

        Args:
            collection_name: Name of the collection
            ids: List of document IDs to update
            documents: Optional new document texts
            metadatas: Optional new metadata
        """
        try:
            collection = self.client.get_collection(collection_name)

            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(f"Updated {len(ids)} documents in {collection_name}")
        except Exception as e:
            logger.error(f"Error updating documents in {collection_name}: {str(e)}")
            raise

    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ) -> None:
        """
        Delete documents from a collection

        Args:
            collection_name: Name of the collection
            ids: List of document IDs to delete
        """
        try:
            collection = self.client.get_collection(collection_name)
            collection.delete(ids=ids)

            logger.info(f"Deleted {len(ids)} documents from {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting documents from {collection_name}: {str(e)}")
            raise

    def get_collection_count(self, collection_name: str) -> int:
        """
        Get the number of documents in a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Number of documents
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            logger.info(f"Collection {collection_name} has {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error getting count for {collection_name}: {str(e)}")
            raise

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete an entire collection

        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            raise

    def list_collections(self) -> List[str]:
        """
        List all collections

        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            names = [c.name for c in collections]
            logger.info(f"Found {len(names)} collections")
            return names
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create VectorStore singleton"""
    global _vector_store

    if _vector_store is None:
        _vector_store = VectorStore()

    return _vector_store
