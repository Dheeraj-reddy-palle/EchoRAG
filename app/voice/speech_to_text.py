import whisper
from app.utils.config import STT_MODEL
from app.utils.logger import logger

logger.info("Loading Whisper STT model: %s", STT_MODEL)
try:
    model = whisper.load_model(STT_MODEL)
except Exception as e:
    logger.error("Failed to load Whisper model: %s", str(e))
    model = None

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio from a file to text using Whisper."""
    if model is None:
        logger.warning("Whisper model not initialized.")
        return ""
        
    logger.info("Transcribing audio file: %s", file_path)
    try:
        result = model.transcribe(file_path)
        text = result.get("text", "").strip()
        logger.info("Successfully transcribed audio.")
        return text
    except Exception as e:
        logger.error("Failed to transcribe audio: %s", str(e))
        return ""
