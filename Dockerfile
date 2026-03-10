FROM python:3.12-slim

WORKDIR /app

# Silence pip root warning
ENV PIP_ROOT_USER_ACTION=ignore

# Only ffmpeg needed now (no espeak, no local whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "launcher.py"]
