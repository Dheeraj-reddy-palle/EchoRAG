FROM python:3.12-slim

WORKDIR /app

# Only ffmpeg needed now (no espeak, no local whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"]
