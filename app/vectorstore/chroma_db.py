import os
import json
from rank_bm25 import BM25Okapi
from app.utils.config import CHROMA_PERSIST_DIR
from app.utils.logger import logger

os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

def _get_project_file(project: str) -> str:
    safe_name = project.lower().replace(" ", "_").replace("-", "_") if project else "default"
    return os.path.join(CHROMA_PERSIST_DIR, f"{safe_name}.json")

def _load_project(project: str) -> dict:
    file_path = _get_project_file(project)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading project {project}: {e}")
    return {"name": project or "default", "chunks": []}

def _save_project(project: str, data: dict):
    file_path = _get_project_file(project)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def store_chunks(chunks: list[dict], project: str = None):
    if not chunks:
        logger.warning("No chunks provided to store.")
        return
    data = _load_project(project)
    data["chunks"].extend(chunks)
    _save_project(project, data)
    logger.info("Stored %d chunks in project '%s'", len(chunks), project or "default")

def create_project(project: str):
    data = _load_project(project)
    _save_project(project, data)
    logger.info("Created project collection: %s", project)

def list_projects() -> list[dict]:
    projects = []
    for filename in os.listdir(CHROMA_PERSIST_DIR):
        if filename.endswith(".json") and filename != "default.json":
            file_path = os.path.join(CHROMA_PERSIST_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    projects.append({"name": data["name"], "chunks": len(data.get("chunks", []))})
            except:
                pass
    return projects

def list_sources(project: str = None) -> list[dict]:
    data = _load_project(project)
    sources = {}
    for chunk in data.get("chunks", []):
        name = chunk.get("metadata", {}).get("source", "Unknown")
        sources[name] = sources.get(name, 0) + 1
    return [{"name": name, "chunks": count} for name, count in sources.items()]

def delete_source(source_name: str, project: str = None):
    data = _load_project(project)
    original_count = len(data.get("chunks", []))
    data["chunks"] = [c for c in data.get("chunks", []) if c.get("metadata", {}).get("source") != source_name]
    _save_project(project, data)
    logger.info("Deleted %d chunks for source '%s'", original_count - len(data["chunks"]), source_name)

def delete_project(project: str):
    file_path = _get_project_file(project)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("Deleted project collection: %s", project)

def query_project(query: str, project: str = None, n_results: int = 3):
    """Fallback BM25 search matching the expected dict signature."""
    data = _load_project(project)
    chunks = data.get("chunks", [])
    if not chunks:
        return {"documents": [[]], "metadatas": [[]]}
    
    # Simple BM25 scoring
    tokenized_corpus = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    
    scores = bm25.get_scores(tokenized_query)
    top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
    
    docs = [chunks[i]["text"] for i in top_n if scores[i] > 0]
    metas = [chunks[i]["metadata"] for i in top_n if scores[i] > 0]
    
    return {"documents": [docs], "metadatas": [metas]}
