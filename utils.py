"""Utility functions for document processing, logging, and embeddings."""

import logging
import hashlib
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from config import LOGS_DIR, AppConfig, PROJECT_ROOT


# Configure logging
def setup_logging(config: AppConfig) -> logging.Logger:
    """Set up logging with the specified configuration."""
    log_file = LOGS_DIR / f"research_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("research_assistant")
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


logger = logging.getLogger("research_assistant")


class DocumentProcessor:
    """Process and chunk documents for indexing."""
    
    @staticmethod
    def load_text_file(file_path: Path, max_chars: int = 800) -> List[Tuple[str, int, str]]:
        """
        Load a text/markdown file and chunk it.
        Returns list of (chunk_text, chunk_id, file_name).
        """
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []
        
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[Tuple[str, int, str]] = []
        current: List[str] = []
        current_len = 0
        chunk_id = 0
        
        for para in paragraphs:
            if current_len + len(para) > max_chars and current:
                chunks.append(("\n\n".join(current), chunk_id, file_path.name))
                chunk_id += 1
                current = []
                current_len = 0
            current.append(para)
            current_len += len(para)
        
        if current:
            chunks.append(("\n\n".join(current), chunk_id, file_path.name))
        
        return chunks
    
    @staticmethod
    def load_pdf_file(file_path: Path, max_chars: int = 800) -> List[Tuple[str, int, str]]:
        """
        Load a PDF file and chunk it.
        Returns list of (chunk_text, chunk_id, file_name).
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.warning("PyPDF2 not installed. Skipping PDF processing.")
            return []
        
        try:
            pdf = PdfReader(file_path)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return []
        
        # Same chunking logic as text files
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[Tuple[str, int, str]] = []
        current: List[str] = []
        current_len = 0
        chunk_id = 0
        
        for para in paragraphs:
            if current_len + len(para) > max_chars and current:
                chunks.append(("\n\n".join(current), chunk_id, file_path.name))
                chunk_id += 1
                current = []
                current_len = 0
            current.append(para)
            current_len += len(para)
        
        if current:
            chunks.append(("\n\n".join(current), chunk_id, file_path.name))
        
        return chunks
    
    @staticmethod
    def iter_documents(data_dir: Path = PROJECT_ROOT / "data") -> List[Path]:
        """Iterate over document files in a directory."""
        if not data_dir.exists():
            logger.warning(f"Data directory '{data_dir}' does not exist.")
            return []
        
        documents = []
        for ext in {".txt", ".md", ".pdf"}:
            documents.extend(data_dir.rglob(f"*{ext}"))
        
        return documents
    
    @staticmethod
    def generate_doc_id(file_path: Path, chunk_id: int) -> str:
        """Generate a unique document ID."""
        rel_path = file_path.relative_to(PROJECT_ROOT)
        return f"{rel_path.as_posix()}::chunk-{chunk_id}"


class EmbeddingCache:
    """Simple in-memory cache for embeddings."""
    
    def __init__(self):
        self._cache = {}
    
    @staticmethod
    def _hash_text(text: str) -> str:
        """Hash text to create a cache key."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> List[float] | None:
        """Get cached embedding if available."""
        key = self._hash_text(text)
        return self._cache.get(key)
    
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding."""
        key = self._hash_text(text)
        self._cache[key] = embedding
    
    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()


class TextCleaner:
    """Utility for cleaning and normalizing text."""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove common artifacts
        text = text.replace("\\n", " ").replace("\\t", " ")
        return text.strip()
    
    @staticmethod
    def truncate(text: str, max_length: int = 500, suffix: str = "...") -> str:
        """Truncate text to a maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
