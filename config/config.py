import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # API Provider Configuration
    API_PROVIDER = os.getenv("API_PROVIDER", "groq")  # "openai", "xai", or "groq"
    API_KEY = os.getenv("API_KEY")

    # LLM Configuration
    if API_PROVIDER == "groq":
        LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    elif API_PROVIDER == "xai":
        LLM_MODEL = os.getenv("LLM_MODEL", "grok-beta")
    else:  # openai
        LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = 0.1  # Low temperature for factual responses

    # Embedding Configuration (free & local)
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384

    # API Base URL
    if API_PROVIDER == "groq":
        API_BASE_URL = "https://api.groq.com/openai/v1"
    elif API_PROVIDER == "xai":
        API_BASE_URL = "https://api.x.ai/v1"
    else:  # openai
        API_BASE_URL = "https://api.openai.com/v1"

    # Vector Store
    VECTOR_STORE_TYPE = "faiss"

    # Retrieval Configuration (TUNED for policy documents)
    CHUNK_SIZE = 500  # Smaller chunks to preserve policy statements
    CHUNK_OVERLAP = 100  # Reduced overlap for better preservation
    TOP_K_RETRIEVAL = 10  # Retrieve more candidates
    SIMILARITY_THRESHOLD = 0.3  # Lower threshold for policy questions

    # Validation Configuration (TUNED for policy documents)
    MIN_SUPPORTING_CHUNKS = 1
    GROUNDING_STRICTNESS = 0.5  # Lower for policy answers that may be interpretive

    # Document Processing
    SUPPORTED_EXTENSIONS = [
        ".pdf"
    ]  # Temporarily disabled image support to prevent processing errors
    OCR_FALLBACK = True

    # Paths
    DATA_RAW_PATH = "data/raw/"
    DATA_PROCESSED_PATH = "data/processed/"
    VECTOR_STORE_PATH = "data/processed/vector_store"

    # Roles
    ALLOWED_ROLES = ["student", "faculty", "coordinator", "parent"]

    # UI
    MAX_CHAT_HISTORY = 10

    # Logging
    LOG_LEVEL = "INFO"
