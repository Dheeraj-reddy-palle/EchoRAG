import requests
import time
from app.utils.config import GROQ_API_KEY, LLM_MODEL
from app.utils.logger import logger

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_TIMEOUT = 30
MAX_RETRIES = 2

def generate_answer(prompt: str) -> str:
    """Sends the prompt to Groq's cloud LLM API with timeout and retry."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY is not set. Please add it to your environment variables."
    
    logger.info("Sending prompt to Groq model: %s", LLM_MODEL)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                GROQ_URL,
                headers=headers,
                json=payload,
                timeout=LLM_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip()
            if answer:
                return answer
            logger.warning("Empty response from Groq on attempt %d", attempt)
        except requests.exceptions.Timeout:
            logger.warning("Groq request timed out (attempt %d/%d)", attempt, MAX_RETRIES)
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Groq API (attempt %d/%d)", attempt, MAX_RETRIES)
        except Exception as e:
            logger.error("LLM error on attempt %d: %s", attempt, str(e))
        
        if attempt < MAX_RETRIES:
            time.sleep(1)
    
    return "Sorry, the AI model is currently unavailable. Please try again in a moment."
