import os
import chromadb
from chromadb.config import Settings
from app.utils.config import CHROMA_PERSIST_DIR
from app.utils.logger import logger
from app.embeddings.embedding_model import get_embeddings

logger.info("Initializing ChromaDB persistent client at %s", CHROMA_PERSIST_DIR)

os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

try:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))
except AttributeError:
    client = chromadb.Client(Settings(persist_directory=CHROMA_PERSIST_DIR, anonymized_telemetry=False))

# Default collection for backward compatibility
collection = client.get_or_create_collection("documents")

def _get_project_collection(project: str):
    """Gets or creates a ChromaDB collection for a specific project."""
    safe_name = project.lower().replace(" ", "_").replace("-", "_")
    return client.get_or_create_collection(safe_name)

def store_chunks(chunks: list[dict], project: str = None):
    """Stores text chunks and their embeddings into ChromaDB."""
    if not chunks:
        logger.warning("No chunks provided to store.")
        return
    
    col = _get_project_collection(project) if project else collection
    
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [f"{chunk['metadata']['source']}_{chunk['metadata']['chunk_id']}" for chunk in chunks]
    
    logger.info("Generating embeddings for %d chunks (project: %s)", len(chunks), project or "default")
    try:
        embeddings = get_embeddings(texts)
    except Exception as e:
        logger.error("Failed to generate embeddings: %s", str(e))
        return
    
    try:
        col.upsert(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)
        logger.info("Stored %d chunks in project '%s'", len(chunks), project or "default")
    except Exception as e:
        logger.error("Failed to store chunks: %s", str(e))

def create_project(project: str):
    """Creates a new empty project collection."""
    safe_name = project.lower().replace(" ", "_").replace("-", "_")
    client.get_or_create_collection(safe_name)
    logger.info("Created project collection: %s", safe_name)

def list_projects() -> list[dict]:
    """Returns all project collections with their document count."""
    try:
        collections = client.list_collections()
        projects = []
        for col in collections:
            if col.name == "documents":
                continue
            projects.append({"name": col.name, "chunks": col.count()})
        return projects
    except Exception as e:
        logger.error("Failed to list projects: %s", str(e))
        return []

def list_sources(project: str = None) -> list[dict]:
    """Returns unique document sources with chunk counts for a project."""
    try:
        col = _get_project_collection(project) if project else collection
        result = col.get(include=["metadatas"])
        sources = {}
        for meta in result.get("metadatas", []):
            name = meta.get("source", "Unknown")
            sources[name] = sources.get(name, 0) + 1
        return [{"name": name, "chunks": count} for name, count in sources.items()]
    except Exception as e:
        logger.error("Failed to list sources: %s", str(e))
        return []

def delete_source(source_name: str, project: str = None):
    """Deletes all chunks belonging to a specific document source."""
    try:
        col = _get_project_collection(project) if project else collection
        result = col.get(include=["metadatas"])
        ids_to_delete = []
        for i, meta in enumerate(result.get("metadatas", [])):
            if meta.get("source") == source_name:
                ids_to_delete.append(result["ids"][i])
        if ids_to_delete:
            col.delete(ids=ids_to_delete)
            logger.info("Deleted %d chunks for '%s' in project '%s'", len(ids_to_delete), source_name, project or "default")
    except Exception as e:
        logger.error("Failed to delete source: %s", str(e))

def delete_project(project: str):
    """Deletes an entire project collection."""
    try:
        safe_name = project.lower().replace(" ", "_").replace("-", "_")
        client.delete_collection(safe_name)
        logger.info("Deleted project collection: %s", safe_name)
    except Exception as e:
        logger.error("Failed to delete project: %s", str(e))

def query_project(query_embedding, project: str = None, n_results: int = 3):
    """Queries a specific project collection."""
    col = _get_project_collection(project) if project else collection
    results = col.query(query_embeddings=[query_embedding], n_results=n_results, include=["documents", "metadatas"])
    return results
