import numpy as np
import pickle
import os
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config.config import Config

# Set environment variables to prevent device issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU


class Embedder:
    def __init__(self):
        self.config = Config()
        # Use TF-IDF for embeddings instead of sentence transformers
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.EMBEDDING_DIMENSION, stop_words="english"
        )
        self.is_fitted = False
        self.vectorizer_path = "data/processed/tfidf_vectorizer.pkl"
        # Try to load existing vectorizer
        self.load_vectorizer()

    def fit_on_texts(self, texts: List[str]) -> None:
        """
        Fit the TF-IDF vectorizer on a corpus of texts.
        This should be called once with all training documents.

        Args:
            texts: List of texts to fit the vectorizer on
        """
        if not self.is_fitted and texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True
            self.save_vectorizer()

    def save_vectorizer(self) -> None:
        """Save the fitted vectorizer to disk."""
        os.makedirs(os.path.dirname(self.vectorizer_path), exist_ok=True)
        with open(self.vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load_vectorizer(self) -> bool:
        """Load the fitted vectorizer from disk."""
        try:
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                self.is_fitted = True
                return True
            return False
        except Exception as e:
            print(f"Failed to load vectorizer: {e}")
            return False

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using TF-IDF.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            if not self.is_fitted:
                # Fit on the texts
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                self.is_fitted = True
            else:
                # Transform new texts
                tfidf_matrix = self.vectorizer.transform(texts)

            # Convert to list of lists
            return tfidf_matrix.toarray().tolist()

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
