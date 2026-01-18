from typing import List, Dict, Any, Optional, Tuple
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from config.config import Config


class Retriever:
    def __init__(self):
        self.config = Config()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        # Load vector store on initialization
        if not self.vector_store.load():
            print("Warning: Vector store not loaded in retriever")

    def retrieve(
        self, query: str, role: Optional[str] = None, top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant chunks for a query with role filtering.

        Args:
            query: User query
            role: User role for filtering (student, faculty, etc.)
            top_k: Number of results to retrieve

        Returns:
            Dict with 'chunks' and 'confidence' keys
        """
        top_k = top_k or self.config.TOP_K_RETRIEVAL

        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        if not query_embedding:
            return {"chunks": [], "confidence": 0.0}

        # Search vector store
        results = self.vector_store.search(
            query_embedding, top_k * 2
        )  # Get more for filtering

        # Filter by role if specified
        if role:
            results = self._filter_by_role(results, role)

        # Filter by similarity threshold
        filtered_results = []
        for chunk, score in results:
            if score >= self.config.SIMILARITY_THRESHOLD:
                filtered_results.append((chunk, score))

        # Sort by score and limit to top_k
        filtered_results.sort(key=lambda x: x[1], reverse=True)
        final_results = filtered_results[:top_k]

        # Calculate confidence based on number of results and average score
        confidence = self._calculate_confidence(final_results)

        chunks = [chunk for chunk, _ in final_results]

        return {
            "chunks": chunks,
            "confidence": confidence,
            "query": query,
            "role": role,
        }

    def _filter_by_role(
        self, results: List[Tuple[Dict[str, Any], float]], role: str
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Filter results based on user role.

        Args:
            results: Search results
            role: User role

        Returns:
            Filtered results
        """
        filtered = []
        for chunk, score in results:
            metadata = chunk.get("metadata", {})
            allowed_roles = metadata.get("allowed_roles", [])

            # If no roles specified, allow all
            if not allowed_roles or role in allowed_roles:
                filtered.append((chunk, score))

        return filtered

    def _calculate_confidence(
        self, results: List[Tuple[Dict[str, Any], float]]
    ) -> float:
        """
        Calculate retrieval confidence based on results.

        Args:
            results: Filtered search results

        Returns:
            Confidence score between 0 and 1
        """
        if not results:
            return 0.0

        num_results = len(results)
        avg_score = sum(score for _, score in results) / num_results

        # Confidence based on number of results and average score
        # Require minimum number of supporting chunks
        if num_results < self.config.MIN_SUPPORTING_CHUNKS:
            return 0.0

        # Normalize score (assuming scores are between 0 and 1)
        confidence = min(avg_score, 1.0)

        return confidence

    def load_vector_store(self) -> bool:
        """
        Load the vector store.

        Returns:
            True if loaded successfully
        """
        return self.vector_store.load()

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get retrieval statistics.
        Ensures vector store is loaded before returning stats.

        Returns:
            Statistics dictionary
        """
        # Ensure vector store is loaded (in case it was updated by ingestion)
        self.vector_store.load()

        return {
            "vector_store_stats": self.vector_store.get_stats(),
            "similarity_threshold": self.config.SIMILARITY_THRESHOLD,
            "min_supporting_chunks": self.config.MIN_SUPPORTING_CHUNKS,
        }
