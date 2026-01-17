import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from config.config import Config


class VectorStore:
    def __init__(self):
        self.config = Config()
        self.index = None
        self.chunks = []
        self.index_path = self.config.VECTOR_STORE_PATH + "_index.faiss"
        self.chunks_path = self.config.VECTOR_STORE_PATH + "_chunks.pkl"

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add chunks with embeddings to the vector store.

        Args:
            chunks: List of chunk dictionaries with 'embedding' key
        """
        if not chunks:
            return

        embeddings = []
        valid_chunks = []

        for chunk in chunks:
            if "embedding" in chunk and chunk["embedding"]:
                embeddings.append(chunk["embedding"])
                valid_chunks.append(chunk)

        if not embeddings:
            return

        embeddings_array = np.array(embeddings, dtype=np.float32)

        if self.index is None:
            # Create new index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatIP(
                dimension
            )  # Inner product (cosine similarity)

        # Add vectors to index
        self.index.add(embeddings_array)
        self.chunks.extend(valid_chunks)

    def search(
        self, query_embedding: List[float], top_k: int = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (chunk, similarity_score) tuples
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        top_k = top_k or self.config.TOP_K_RETRIEVAL

        query_array = np.array([query_embedding], dtype=np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(query_array)

        # Search
        scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                chunk = self.chunks[idx]
                results.append((chunk, float(score)))

        return results

    def save(self) -> None:
        """
        Save the vector store to disk.
        """
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)

        with open(self.chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self) -> bool:
        """
        Load the vector store from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)

            if os.path.exists(self.chunks_path):
                with open(self.chunks_path, "rb") as f:
                    self.chunks = pickle.load(f)

            return self.index is not None and len(self.chunks) > 0
        except Exception as e:
            print(f"Failed to load vector store: {str(e)}")
            return False

    def clear(self) -> None:
        """
        Clear the vector store.
        """
        self.index = None
        self.chunks = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.chunks_path):
            os.remove(self.chunks_path)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with stats
        """
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.config.EMBEDDING_DIMENSION,
        }
