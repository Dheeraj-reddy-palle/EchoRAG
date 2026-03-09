# 🗣️ EchoRAG — Voice-Enabled RAG Assistant

A modular, voice-enabled Retrieval-Augmented Generation (RAG) assistant that lets you upload documents, create topic-specific projects, and ask questions via text or voice — all powered by local AI.

## Features

- **Project-Based Knowledge** — Create isolated projects (e.g., Physics, Biology) with their own document collections
- **Document Ingestion** — Upload PDFs and TXT files, automatically chunked and embedded
- **Semantic Search** — ChromaDB vector store with sentence-transformer embeddings
- **Voice Input** — Record voice queries transcribed by OpenAI Whisper
- **Local LLM** — Ollama-powered inference with Phi-3 (no cloud APIs required)
- **Premium Dark UI** — Streamlit frontend with glassmorphism, gradient theme, and project manager

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐
│  Streamlit   │───▶│  FastAPI      │───▶│  Ollama   │
│  Frontend    │◀───│  Backend     │◀───│  (Phi-3)  │
└─────────────┘    └──────┬───────┘    └───────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌─────────┐ ┌─────────┐
        │ ChromaDB │ │ Whisper │ │ MiniLM  │
        │ Vectors  │ │  STT    │ │ Embedder│
        └──────────┘ └─────────┘ └─────────┘
```

## Project Structure

```
EchoRAG/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/routes.py           # API endpoints
│   ├── embeddings/embedding_model.py
│   ├── frontend/streamlit_app.py
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   ├── text_extractor.py
│   │   └── chunking.py
│   ├── llm/llm_engine.py      # Ollama client with timeout/retry
│   ├── rag/
│   │   ├── rag_pipeline.py
│   │   └── prompt_builder.py
│   ├── retrieval/retriever.py
│   ├── utils/
│   │   ├── config.py
│   │   └── logger.py
│   ├── vectorstore/chroma_db.py
│   └── voice/
│       ├── speech_to_text.py
│       └── text_to_speech.py
├── .streamlit/config.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

- **Python 3.12+**
- **Ollama** — Local LLM runtime
- **ffmpeg** — Required by Whisper for audio decoding
- **macOS** (for native TTS via `say` command)

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/EchoRAG.git
cd EchoRAG

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install system deps (macOS)
brew install ollama ffmpeg

# 5. Start Ollama and pull the model
brew services start ollama
ollama pull phi3

# 6. Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 7. Start the frontend (new terminal)
streamlit run app/frontend/streamlit_app.py --server.port 8501
```

Open `http://localhost:8501` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload?project=` | Upload document to a project |
| POST | `/ask` | Ask a question (text) |
| GET | `/projects` | List all projects |
| POST | `/projects/create?name=` | Create a new project |
| DELETE | `/projects/{name}` | Delete a project |
| GET | `/documents?project=` | List documents in a project |
| DELETE | `/documents/{name}?project=` | Delete a document |
| POST | `/voice/transcribe` | Transcribe audio to text |
| POST | `/voice/ask` | Full voice query pipeline |

## Configuration

Edit `app/utils/config.py`:

```python
MODEL_NAME = "phi3"           # Ollama model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3                     # Chunks to retrieve
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
STT_MODEL = "base"            # Whisper model size
```

## License

MIT
