from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.config import CHUNK_SIZE, CHUNK_OVERLAP

def split_text_into_chunks(text: str, source: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Splits raw text into manageable, overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    docs = splitter.create_documents([text])
    chunks = []
    
    for i, doc in enumerate(docs):
        # Attach metadata to each document fraction for citations
        metadata = {
            "source": source,
            "chunk_id": f"chunk_{i+1}"
        }
        chunks.append({"text": doc.page_content, "metadata": metadata})
        
    return chunks
