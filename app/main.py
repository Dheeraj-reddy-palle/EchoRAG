from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI app."""
    logger.info("Starting up EchoRAG API Server...")
    yield
    logger.info("Shutting down EchoRAG API Server...")

app = FastAPI(
    title="EchoRAG API",
    description="Voice-enabled RAG Assistant API",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "EchoRAG is running"}
