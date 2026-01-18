import numpy as np
from typing import List, Dict, Any
from openai import OpenAI
from config.config import Config


class Embedder:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            response = self.client.embeddings.create(
                input=texts, model=self.config.EMBEDDING_MODEL
            )

            embeddings = [data.embedding for data in response.data]

            # Validate embedding dimensions
            expected_dim = self.config.EMBEDDING_DIMENSION
            for i, emb in enumerate(embeddings):
                if len(emb) != expected_dim:
                    raise ValueError(
                        f"Embedding {i} has dimension {len(emb)}, expected {expected_dim}"
                    )

            return embeddings

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
