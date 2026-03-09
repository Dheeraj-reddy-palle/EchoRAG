import subprocess
import os
import time
from app.utils.logger import logger

def synthesize_speech(text: str, output_file: str | None = None) -> str:
    """Synthesizes text to speech using macOS native 'say' command and saves to a WAV file."""
    if not output_file:
        os.makedirs("temp_audio", exist_ok=True)
        output_file = f"temp_audio/response_{int(time.time())}.wav"
        
    logger.info("Synthesizing speech to %s", output_file)
    try:
        subprocess.run([
            "say", text, 
            "--data-format=LEI16@44100", 
            "-o", output_file
        ], check=True)
        
        logger.info("Successfully generated speech audio at %s", output_file)
        return output_file
    except Exception as e:
        logger.error("Failed to synthesize speech: %s", str(e))
        return ""
