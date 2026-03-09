import requests
from app.utils.config import GROQ_API_KEY
from app.utils.logger import logger

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio using Groq's Whisper API (cloud-based, no local model needed)."""
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set.")
        return ""
    
    logger.info("Transcribing audio via Groq Whisper API: %s", file_path)
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        with open(file_path, "rb") as audio_file:
            files = {"file": (file_path, audio_file, "audio/wav")}
            data = {"model": "whisper-large-v3-turbo", "language": "en"}
            response = requests.post(
                GROQ_WHISPER_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        response.raise_for_status()
        text = response.json().get("text", "").strip()
        logger.info("Successfully transcribed audio.")
        return text
    except Exception as e:
        logger.error("Failed to transcribe audio: %s", str(e))
        return ""
