from app.vectorstore.chroma_db import query_project
from app.utils.config import TOP_K
from app.utils.logger import logger

def get_relevant_chunks(query: str, project: str = None) -> list[dict]:
    """Retrieves the top k most relevant chunks from the BM25 store for a given query."""
    logger.info("Retrieving top %s chunks for query: %s (project: %s)", TOP_K, query, project or "default")
    
    try:
        # Pass the raw text query directly (BM25 handles tokenization)
        results = query_project(query, project=project, n_results=TOP_K)
        
        if not results or "documents" not in results or not results["documents"][0]:
            logger.warning("No documents retrieved.")
            return []
            
        chunks = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append({"text": doc, "metadata": meta})
            
        logger.info("Successfully retrieved %d chunks", len(chunks))
        return chunks
        
    except Exception as e:
        logger.error("Failed to query database: %s", str(e))
        return []
