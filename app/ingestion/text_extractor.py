import os
import pypdf
from app.utils.logger import logger

def extract_text_from_file(file_path: str) -> str:
    """Extracts raw text from PDF or TXT files."""
    logger.info("Extracting text from: %s", file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            logger.error("Failed to read PDF %s: %s", file_path, str(e))
        return text.strip()
    
    elif ext == ".txt":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error("Failed to read text file %s: %s", file_path, str(e))
            return ""
    
    else:
        logger.warning("Unsupported file format: %s", ext)
        return ""
