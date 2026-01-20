import numpy as np
import pickle
import os
import torch
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from config.config import Config

# Force CPU tensors to avoid meta tensor issues
torch.set_default_dtype(torch.float32)
torch.set_default_device("cpu")

# Set environment variables to prevent device issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU

class Embedder:
    def __init__(self):
        self.config = Config()

        # Initialize the model first
        try:
            print(f"Loading model: {self.config.EMBEDDING_MODEL} on CPU")
            self.model = SentenceTransformer(self.config.EMBEDDING_MODEL)
            self.model.to("cpu")  # Explicitly move model to CPU after loading
        except Exception as e:
            raise RuntimeError(f"Failed to load SentenceTransformer model: {str(e)}")

        self.model_path = "data/processed/sentence_transformer.pkl"
        # Sentence transformers don't need fitting, but we can save/load if needed

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Sentence Transformers.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
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

    # Legacy methods for compatibility
    def fit_on_texts(self, texts: List[str]) -> None:
        pass  # Not needed for sentence transformers

    def save_vectorizer(self) -> None:
        pass

    def load_vectorizer(self) -> bool:
        return True
