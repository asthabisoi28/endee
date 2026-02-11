"""Configuration management for the AI Research Assistant."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


@dataclass
class EndeeConfig:
    """Configuration for Endee vector database."""
    base_url: str
    token: Optional[str]
    index_name: str
    vector_dim: int
    space_type: str = "cosine"  # Options: cosine, l2, ip


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""
    model_name: str
    batch_size: int = 32
    device: str = "cpu"  # Options: cpu, cuda, mps


@dataclass
class LLMConfig:
    """Configuration for Large Language Models."""
    provider: str  # Options: openai, anthropic, ollama
    model_name: str
    api_key: Optional[str]
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class AppConfig:
    """Main application configuration."""
    endee: EndeeConfig
    embedding: EmbeddingConfig
    llm: LLMConfig
    
    # Retrieval settings
    top_k: int = 5
    similarity_threshold: float = 0.3
    
    # Indexing settings
    chunk_size: int = 800
    chunk_overlap: int = 100
    
    # Logging
    log_level: str = "INFO"
    debug: bool = False


def load_config() -> AppConfig:
    """Load configuration from environment variables and .env file."""
    load_dotenv(PROJECT_ROOT / ".env")
    
    # Endee configuration
    endee_config = EndeeConfig(
        base_url=os.getenv("ENDEE_BASE_URL", "http://localhost:8080/api/v1"),
        token=os.getenv("ENDEE_TOKEN"),
        index_name=os.getenv("ENDEE_INDEX_NAME", "research_assistant"),
        vector_dim=int(os.getenv("VECTOR_DIM", "384")),
        space_type=os.getenv("SPACE_TYPE", "cosine"),
    )
    
    # Embedding configuration
    embedding_config = EmbeddingConfig(
        model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
        device=os.getenv("EMBEDDING_DEVICE", "cpu"),
    )
    
    # LLM configuration
    llm_config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model_name=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
    )
    
    # Application configuration
    app_config = AppConfig(
        endee=endee_config,
        embedding=embedding_config,
        llm=llm_config,
        top_k=int(os.getenv("TOP_K", "5")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.3")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
    
    return app_config
