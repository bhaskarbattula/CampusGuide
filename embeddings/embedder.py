from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from config.config import Config
from utils.logger import logger


class Embedder:
    def __init__(self):
        self.config = Config()

        # 🔧 CRITICAL FIX: Explicit device control (prevents meta tensor crash)
        self.device = "cpu"

        logger.info(
            f"Loading embedding model '{self.config.EMBEDDING_MODEL}' on device: {self.device}"
        )

        # Disable auto device transfer inside SentenceTransformer
        self.model = SentenceTransformer(
            self.config.EMBEDDING_MODEL,
            device=self.device
        )

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
            embeddings = self.model.encode(
                texts,
                batch_size=16,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            embeddings_list = embeddings.tolist()

            expected_dim = self.config.EMBEDDING_DIMENSION
            for i, emb in enumerate(embeddings_list):
                if len(emb) != expected_dim:
                    raise ValueError(
                        f"Embedding {i} has dimension {len(emb)}, expected {expected_dim}"
                    )

            return embeddings_list

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
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
        embedding = self.embed_texts([query])
        return embedding[0] if embedding else []
