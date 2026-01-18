from typing import Dict, Any
from config.config import Config


class SafetyChecker:
    def __init__(self):
        self.config = Config()

    def check_retrieval_safety(
        self, retrieval_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if retrieval results meet safety thresholds.

        Args:
            retrieval_result: Result from retriever with 'chunks' and 'confidence'

        Returns:
            Dict with 'safe' boolean and reasoning
        """
        chunks = retrieval_result.get("chunks", [])
        confidence = retrieval_result.get("confidence", 0.0)

        # Check minimum number of supporting chunks
        if len(chunks) < self.config.MIN_SUPPORTING_CHUNKS:
            return {
                "safe": False,
                "reason": f"Insufficient supporting chunks. Found {len(chunks)}, required {self.config.MIN_SUPPORTING_CHUNKS}",
                "chunks_count": len(chunks),
                "confidence": confidence,
            }

        # Check confidence threshold
        if confidence < self.config.SIMILARITY_THRESHOLD:
            return {
                "safe": False,
                "reason": f"Retrieval confidence too low. Score {confidence:.3f}, required {self.config.SIMILARITY_THRESHOLD}",
                "chunks_count": len(chunks),
                "confidence": confidence,
            }

        # Additional checks
        if not self._has_diverse_sources(chunks):
            return {
                "safe": False,
                "reason": "Retrieved chunks lack source diversity",
                "chunks_count": len(chunks),
                "confidence": confidence,
            }

        return {
            "safe": True,
            "reason": "Retrieval meets safety criteria",
            "chunks_count": len(chunks),
            "confidence": confidence,
        }

    def _has_diverse_sources(self, chunks: list) -> bool:
        """
        Check if chunks come from diverse sources/pages.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            True if sources are diverse enough
        """
        if len(chunks) < 2:
            return True  # Single chunk is acceptable

        sources = set()
        pages = set()

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            filename = metadata.get("filename", "unknown")
            chunk_pages = chunk.get("pages", [])

            sources.add(filename)
            pages.update(chunk_pages)

        # Allow single source if we have sufficient chunks
        return len(sources) >= 1

    def get_safety_stats(self) -> Dict[str, Any]:
        """
        Get current safety thresholds.

        Returns:
            Dictionary with safety parameters
        """
        return {
            "min_supporting_chunks": self.config.MIN_SUPPORTING_CHUNKS,
            "similarity_threshold": self.config.SIMILARITY_THRESHOLD,
            "require_diverse_sources": True,
        }
