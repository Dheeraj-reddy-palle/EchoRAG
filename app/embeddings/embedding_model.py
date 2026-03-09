from sentence_transformers import SentenceTransformer
from app.utils.config import EMBEDDING_MODEL
from app.utils.logger import logger

logger.info("Loading embedding model %s", EMBEDDING_MODEL)
model = SentenceTransformer(EMBEDDING_MODEL)

def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for a given text."""
    return model.encode(text).tolist()

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embedding vectors for a list of texts."""
    return model.encode(texts).tolist()
