import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # API Provider Configuration
    API_PROVIDER = os.getenv("API_PROVIDER", "groq")  # "openai", "xai", or "groq"
    API_KEY = (
        os.getenv("OPENAI_API_KEY")
        if API_PROVIDER == "openai"
        else os.getenv("GROQ_API_KEY")
        if API_PROVIDER == "groq"
        else os.getenv("API_KEY")
    )

    # LLM Configuration
    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "grok-beta"
        if API_PROVIDER == "xai"
        else "llama-3.1-8b-instant"
        if API_PROVIDER == "groq"
        else "gpt-3.5-turbo",
    )
    LLM_TEMPERATURE = 0.1  # Low temperature for factual responses

    # Embedding Configuration (TF-IDF based)
    EMBEDDING_DIMENSION = 1000  # Max features for TF-IDF

    # API Base URL
    API_BASE_URL = (
        "https://api.x.ai/v1"
        if API_PROVIDER == "xai"
        else "https://api.groq.com/openai/v1"
        if API_PROVIDER == "groq"
        else "https://api.openai.com/v1"
    )

    # Vector Store
    VECTOR_STORE_TYPE = "faiss"

    # Retrieval Configuration (TUNED for policy documents)
    CHUNK_SIZE = 1500  # Larger chunks to keep sentences together
    CHUNK_OVERLAP = 500  # Increased overlap for better continuity
    TOP_K_RETRIEVAL = 15  # Retrieve more candidates
    SIMILARITY_THRESHOLD = 0.1  # Lower threshold for policy questions

    # Validation Configuration (TUNED for policy documents)
    MIN_SUPPORTING_CHUNKS = 1
    GROUNDING_STRICTNESS = 0.3  # Lower for policy answers that may be interpretive

    # Document Processing
    SUPPORTED_EXTENSIONS = [".pdf", ".txt"]  # Support PDF and TXT files
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
