import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # API Provider Configuration
    API_PROVIDER = os.getenv("API_PROVIDER", "groq")  # "openai", "xai", or "groq"
<<<<<<< HEAD
    API_KEY = os.getenv("API_KEY")

    # LLM Configuration
    if API_PROVIDER == "groq":
        LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    elif API_PROVIDER == "xai":
        LLM_MODEL = os.getenv("LLM_MODEL", "grok-beta")
    else:  # openai
        LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
=======
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
>>>>>>> bhaskar
    LLM_TEMPERATURE = 0.1  # Low temperature for factual responses

    # Embedding Configuration (TF-IDF based)
    EMBEDDING_DIMENSION = 1000  # Max features for TF-IDF

    # API Base URL
<<<<<<< HEAD
    if API_PROVIDER == "groq":
        API_BASE_URL = "https://api.groq.com/openai/v1"
    elif API_PROVIDER == "xai":
        API_BASE_URL = "https://api.x.ai/v1"
    else:  # openai
        API_BASE_URL = "https://api.openai.com/v1"
=======
    API_BASE_URL = (
        "https://api.x.ai/v1"
        if API_PROVIDER == "xai"
        else "https://api.groq.com/openai/v1"
        if API_PROVIDER == "groq"
        else "https://api.openai.com/v1"
    )
>>>>>>> bhaskar

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
<<<<<<< HEAD
    SUPPORTED_EXTENSIONS = [".txt"]  # Plain text files only
=======
    SUPPORTED_EXTENSIONS = [".pdf", ".txt"]  # Support PDF and TXT files
    OCR_FALLBACK = True
>>>>>>> bhaskar

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
