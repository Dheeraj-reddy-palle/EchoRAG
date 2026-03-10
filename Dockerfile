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

# Command to run both API and Streamlit. 
# We use 'wait -n' so if either process crashes (e.g. backend OOM), the entire container restarts cleanly.
CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true & wait -n; exit 1"]
