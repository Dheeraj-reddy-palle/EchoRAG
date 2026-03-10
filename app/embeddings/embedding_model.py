from app.utils.logger import logger

def get_embedding(text: str) -> list[float]:
    """Stub: Embeddings are no longer used. Switched to lightweight BM25 retrieval."""
    logger.warning("get_embedding called but embeddings are disabled for cloud memory optimization.")
    return []

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Stub: Embeddings are no longer used."""
    return [[] for _ in texts]
