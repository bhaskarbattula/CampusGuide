import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = 0.1  # Low temperature for factual responses
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = 1536  # For text-embedding-ada-002

    # Vector Store Configuration
    VECTOR_STORE_TYPE = "faiss"  # or "chromadb"

    # Retrieval Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RETRIEVAL = 5
    SIMILARITY_THRESHOLD = 0.7  # Minimum similarity for retrieval confidence

    # Validation Configuration
    MIN_SUPPORTING_CHUNKS = 2  # Minimum chunks required for answer
    GROUNDING_STRICTNESS = 0.8  # Threshold for grounding validation

    # Document Processing
    SUPPORTED_EXTENSIONS = [".pdf"]
    OCR_FALLBACK = True

    # Paths
    DATA_RAW_PATH = "data/raw/"
    DATA_PROCESSED_PATH = "data/processed/"
    VECTOR_STORE_PATH = "data/processed/vector_store"

    # Roles
    ALLOWED_ROLES = ["student", "faculty", "coordinator", "parent"]

    # UI Configuration
    MAX_CHAT_HISTORY = 10

    # Logging
    LOG_LEVEL = "INFO"
