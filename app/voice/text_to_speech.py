import os
import time
from gtts import gTTS
from app.utils.logger import logger

def synthesize_speech(text: str, output_file: str | None = None) -> str:
    """Synthesizes text to speech using gTTS (works on all platforms, including cloud)."""
    if not output_file:
        os.makedirs("temp_audio", exist_ok=True)
        output_file = f"temp_audio/response_{int(time.time())}.mp3"
        
    logger.info("Synthesizing speech to %s", output_file)
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_file)
        logger.info("Successfully generated speech audio at %s", output_file)
        return output_file
    except Exception as e:
        logger.error("Failed to synthesize speech: %s", str(e))
        return ""
