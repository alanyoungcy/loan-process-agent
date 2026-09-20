"""
RAG (Retrieval-Augmented Generation) Service
Handles context retrieval for GenAI prompts
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib

from app.services.genai.vector_store import get_vector_store
from app.services.genai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG service for retrieving relevant context from knowledge base
    """

    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()

        # Collection names
        self.COMPLIANCE_COLLECTION = "compliance_policies"
        self.SCRIPT_TEMPLATES_COLLECTION = "script_templates"
        self.CASE_HISTORY_COLLECTION = "case_history"
        self.OBJECTIONS_COLLECTION = "customer_objections"

    async def retrieve_context(
        self,
        query: str,
        collection: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from a collection

        Args:
            query: Query text
            collection: Collection name
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            List of context dicts with document, metadata, distance
        """
        try:
            results = self.vector_store.query(
                collection_name=collection,
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            # Format results
            contexts = []
            if results and results.get('ids') and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    contexts.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })

            logger.info(
                f"Retrieved {len(contexts)} contexts from {collection} for query: {query[:50]}..."
            )

            return contexts

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []

    async def retrieve_compliance_context(
        self,
        query: str,
        n_results: int = 3
    ) -> str:
        """
        Retrieve HK compliance regulations context

        Args:
            query: Query text
            n_results: Number of results

        Returns:
            Formatted context string
        """
        contexts = await self.retrieve_context(
            query=query,
            collection=self.COMPLIANCE_COLLECTION,
            n_results=n_results
        )

        if not contexts:
            return "No compliance context found."

        formatted = "=== HONG KONG COMPLIANCE REGULATIONS ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            source = ctx['metadata'].get('source', 'Unknown')
            doc = ctx['document']
            formatted += f"[{i}] Source: {source}\n{doc}\n\n"

        return formatted

    async def retrieve_script_templates(
        self,
        scenario: str,
        n_results: int = 2
    ) -> str:
        """
        Retrieve approved script templates

        Args:
            scenario: Collection scenario (e.g., "first_contact", "payment_plan")
            n_results: Number of templates

        Returns:
            Formatted templates string
        """
        contexts = await self.retrieve_context(
            query=f"{scenario} collection script",
            collection=self.SCRIPT_TEMPLATES_COLLECTION,
            n_results=n_results,
            where={"scenario": scenario} if scenario else None
        )

        if not contexts:
            return "No script templates found."

        formatted = "=== APPROVED SCRIPT TEMPLATES ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            scenario_name = ctx['metadata'].get('scenario', 'General')
            effectiveness = ctx['metadata'].get('effectiveness_score', 'N/A')
            doc = ctx['document']
            formatted += f"[{i}] Scenario: {scenario_name} (Effectiveness: {effectiveness})\n{doc}\n\n"

        return formatted

    async def retrieve_similar_cases(
        self,
        case_description: str,
        n_results: int = 3
    ) -> str:
        """
        Retrieve similar historical cases

        Args:
            case_description: Description of current case
            n_results: Number of similar cases

        Returns:
            Formatted case history string
        """
        contexts = await self.retrieve_context(
            query=case_description,
            collection=self.CASE_HISTORY_COLLECTION,
            n_results=n_results
        )

        if not contexts:
            return "No similar cases found."

        formatted = "=== SIMILAR HISTORICAL CASES ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            case_id = ctx['metadata'].get('case_id', 'Unknown')
            outcome = ctx['metadata'].get('outcome', 'N/A')
            doc = ctx['document']
            formatted += f"[{i}] Case: {case_id} (Outcome: {outcome})\n{doc}\n\n"

        return formatted

    async def retrieve_objection_responses(
        self,
        objection: str,
        n_results: int = 2
    ) -> str:
        """
        Retrieve effective responses to customer objections

        Args:
            objection: Customer objection text
            n_results: Number of responses

        Returns:
            Formatted objection responses
        """
        contexts = await self.retrieve_context(
            query=objection,
            collection=self.OBJECTIONS_COLLECTION,
            n_results=n_results
        )

        if not contexts:
            return "No objection responses found."

        formatted = "=== EFFECTIVE OBJECTION RESPONSES ===\n\n"
        for i, ctx in enumerate(contexts, 1):
            objection_type = ctx['metadata'].get('objection_type', 'General')
            success_rate = ctx['metadata'].get('success_rate', 'N/A')
            doc = ctx['document']
            formatted += f"[{i}] Type: {objection_type} (Success Rate: {success_rate})\n{doc}\n\n"

        return formatted

    async def hybrid_search(
        self,
        query: str,
        collections: List[str],
        n_results_per_collection: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple collections

        Args:
            query: Query text
            collections: List of collection names
            n_results_per_collection: Results per collection

        Returns:
            Dict mapping collection names to results
        """
        results = {}

        for collection in collections:
            try:
                contexts = await self.retrieve_context(
                    query=query,
                    collection=collection,
                    n_results=n_results_per_collection
                )
                results[collection] = contexts
            except Exception as e:
                logger.error(f"Error searching {collection}: {str(e)}")
                results[collection] = []

        return results

    def calculate_relevance_score(self, distance: float) -> float:
        """
        Convert distance to relevance score (0-1)

        Args:
            distance: Distance from query

        Returns:
            Relevance score (higher is more relevant)
        """
        # Cosine distance is 0-2, convert to relevance 0-1
        return max(0.0, 1.0 - (distance / 2.0))

    async def get_augmented_prompt(
        self,
        base_query: str,
        include_compliance: bool = True,
        include_templates: bool = False,
        include_cases: bool = False,
        scenario: Optional[str] = None
    ) -> str:
        """
        Build augmented prompt with retrieved context

        Args:
            base_query: Base user query
            include_compliance: Include compliance context
            include_templates: Include script templates
            include_cases: Include similar cases
            scenario: Scenario for template retrieval

        Returns:
            Augmented prompt with context
        """
        augmented = f"USER QUERY:\n{base_query}\n\n"

        if include_compliance:
            compliance_ctx = await self.retrieve_compliance_context(
                query=base_query,
                n_results=3
            )
            augmented += compliance_ctx + "\n"

        if include_templates and scenario:
            templates_ctx = await self.retrieve_script_templates(
                scenario=scenario,
                n_results=2
            )
            augmented += templates_ctx + "\n"

        if include_cases:
            cases_ctx = await self.retrieve_similar_cases(
                case_description=base_query,
                n_results=2
            )
            augmented += cases_ctx + "\n"

        return augmented


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAGService singleton"""
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()

    return _rag_service
