# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (required for pyttsx3 and whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak \
    libespeak1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Command to run both the API and Streamlit (For complete containerization)
# In a real microservice, you would split these, but here we run them via a shell script
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
