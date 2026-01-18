import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from config.config import Config


class Embedder:
    def __init__(self):
        self.config = Config()
        # Use free sentence transformer model (no API key needed)
        self.model = SentenceTransformer(self.config.EMBEDDING_MODEL)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using sentence transformers.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            # Generate embeddings using sentence transformers
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            # Convert to list of lists and normalize
            embeddings_list = embeddings.tolist()

            # Validate embedding dimensions
            expected_dim = self.config.EMBEDDING_DIMENSION
            for i, emb in enumerate(embeddings_list):
                if len(emb) != expected_dim:
                    raise ValueError(
                        f"Embedding {i} has dimension {len(emb)}, expected {expected_dim}"
                    )

            return embeddings_list

        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks and add to chunk metadata.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of chunks with embeddings added
        """
        if not chunks:
            return []

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embed_texts(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else []
