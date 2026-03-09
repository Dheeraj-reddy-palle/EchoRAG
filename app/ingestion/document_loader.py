import os
from app.utils.logger import logger
from app.ingestion.text_extractor import extract_text_from_file
from app.ingestion.chunking import split_text_into_chunks

def process_document(file_path: str, source_name: str = None) -> list[dict]:
    """Orchestrates extraction and chunking of a single document."""
    if not source_name:
        source_name = os.path.basename(file_path)
        
    logger.info("Starting ingestion for document: %s", source_name)
    
    text = extract_text_from_file(file_path)
    if not text:
        logger.warning("Document ingestion yielded empty text for %s", source_name)
        return []
        
    chunks = split_text_into_chunks(text, source_name)
    logger.info("Successfully produced %d chunks for %s", len(chunks), source_name)
    
    return chunks
