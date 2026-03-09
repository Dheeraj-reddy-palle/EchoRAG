import os

# Groq API (free cloud LLM + Whisper)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.1-8b-instant")

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG settings
TOP_K = 3
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Storage
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_storage")
