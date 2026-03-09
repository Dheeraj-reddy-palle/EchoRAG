import requests
import time
from app.utils.config import OLLAMA_URL, MODEL_NAME
from app.utils.logger import logger

LLM_TIMEOUT = 120  # seconds
MAX_RETRIES = 2

def generate_answer(prompt: str) -> str:
    """Sends the context-enriched prompt to the local LLM via Ollama API with timeout and retry."""
    logger.info("Sending prompt to LLM model: %s", MODEL_NAME)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=LLM_TIMEOUT
            )
            response.raise_for_status()
            answer = response.json().get("response", "").strip()
            if answer:
                return answer
            logger.warning("Empty response from LLM on attempt %d", attempt)
        except requests.exceptions.Timeout:
            logger.warning("LLM request timed out (attempt %d/%d)", attempt, MAX_RETRIES)
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama at %s (attempt %d/%d)", OLLAMA_URL, attempt, MAX_RETRIES)
        except Exception as e:
            logger.error("LLM error on attempt %d: %s", attempt, str(e))
        
        if attempt < MAX_RETRIES:
            time.sleep(2)
    
    return "Sorry, the AI model is currently unavailable. Please try again in a moment."
