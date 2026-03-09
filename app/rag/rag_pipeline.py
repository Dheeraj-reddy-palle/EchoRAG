from app.retrieval.retriever import get_relevant_chunks
from app.rag.prompt_builder import build_rag_prompt
from app.llm.llm_engine import generate_answer
from app.utils.logger import logger

def ask_question(query: str, project: str = None) -> str:
    """Orchestrates retrieval of documents and generation of a response based on a query."""
    logger.info("Running RAG pipeline for query: '%s' (project: %s)", query, project or "default")
    
    retrieved_chunks = get_relevant_chunks(query, project=project)
    
    if not retrieved_chunks:
        logger.info("No relevant chunks found. Falling back to generic conversational model.")
        
    prompt = build_rag_prompt(query, retrieved_chunks)
    answer = generate_answer(prompt)
    
    logger.info("Successfully generated RAG answer.")
    return answer
