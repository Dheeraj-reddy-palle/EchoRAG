from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from starlette.responses import FileResponse
import shutil
import os
import tempfile
from app.utils.logger import logger
from app.ingestion.document_loader import process_document
from app.vectorstore.chroma_db import store_chunks, list_sources, delete_source, list_projects, delete_project, create_project
from app.rag.rag_pipeline import ask_question
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    project: Optional[str] = None

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), project: str = Query(None)):
    logger.info("Received upload: %s (project: %s)", file.filename, project or "default")
    file_path = ""
    try:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        chunks = process_document(file_path, file.filename)
        store_chunks(chunks, project=project)
        
        return {"filename": file.filename, "chunks_processed": len(chunks)}
    except Exception as e:
        logger.error("Error processing document %s: %s", file.filename, str(e))
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

@router.post("/ask")
async def ask_rag(request: QueryRequest):
    logger.info("Received query: %s (project: %s)", request.query, request.project or "default")
    answer = ask_question(request.query, project=request.project)
    return {"query": request.query, "answer": answer}

@router.get("/projects")
async def get_projects():
    projects = list_projects()
    return {"projects": projects}

@router.post("/projects/create")
async def create_new_project(name: str = Query(...)):
    logger.info("Creating project: %s", name)
    create_project(name)
    return {"status": "created", "project": name}

@router.get("/documents")
async def get_documents(project: str = Query(None)):
    sources = list_sources(project=project)
    return {"documents": sources}

@router.delete("/documents/{source_name}")
async def remove_document(source_name: str, project: str = Query(None)):
    logger.info("Deleting document: %s (project: %s)", source_name, project or "default")
    delete_source(source_name, project=project)
    return {"status": "deleted", "source": source_name}

@router.delete("/projects/{project_name}")
async def remove_project(project_name: str):
    logger.info("Deleting entire project: %s", project_name)
    delete_project(project_name)
    return {"status": "deleted", "project": project_name}

@router.post("/voice/transcribe")
async def transcribe_only(audio_file: UploadFile = File(...)):
    logger.info("Received voice transcription request")
    file_path = ""
    try:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, audio_file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        text = transcribe_audio(file_path)
        logger.info("Transcribed text: %s", text)
        
        return {"transcription": text}
    except Exception as e:
        logger.error("Error processing transcription: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

@router.post("/voice/ask")
async def ask_voice(audio_file: UploadFile = File(...)):
    logger.info("Received voice query")
    try:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, audio_file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        query = transcribe_audio(file_path)
        logger.info("Transcribed query: %s", query)
        
        answer = ask_question(query)
        
        audio_response_path = synthesize_speech(answer)
        
        return FileResponse(audio_response_path, media_type="audio/wav", filename="response.wav")
    except Exception as e:
        logger.error("Error processing voice query: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
