"""Document indexing pipeline."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import AppConfig, PROJECT_ROOT
from retriever import SemanticSearchEngine
from utils import DocumentProcessor, logger


class DocumentIndexer:
    """Index documents into the semantic search engine."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.search_engine = SemanticSearchEngine(config)
        self.processor = DocumentProcessor()
    
    def index_directory(
        self,
        data_dir: Optional[Path] = None,
        recursive: bool = True
    ) -> int:
        """Index all documents in a directory."""
        data_dir = data_dir or (PROJECT_ROOT / "data")
        
        if not data_dir.exists():
            logger.warning(f"Data directory '{data_dir}' does not exist. Creating it...")
            data_dir.mkdir(parents=True, exist_ok=True)
            return 0
        
        logger.info(f"Indexing documents from: {data_dir}")
        
        documents = []
        
        # Load text files
        for file_path in data_dir.rglob("*.txt" if recursive else "*.txt"):
            if file_path.is_file():
                logger.info(f"Processing: {file_path.name}")
                chunks = self.processor.load_text_file(
                    file_path,
                    max_chars=self.config.chunk_size
                )
                
                for chunk_text, chunk_id, file_name in chunks:
                    doc = {
                        "id": f"{file_name}::chunk-{chunk_id}",
                        "text": chunk_text,
                        "source": file_name,
                        "chunk_id": chunk_id,
                    }
                    documents.append(doc)
        
        # Load markdown files
        for file_path in data_dir.rglob("*.md" if recursive else "*.md"):
            if file_path.is_file():
                logger.info(f"Processing: {file_path.name}")
                chunks = self.processor.load_text_file(
                    file_path,
                    max_chars=self.config.chunk_size
                )
                
                for chunk_text, chunk_id, file_name in chunks:
                    doc = {
                        "id": f"{file_name}::chunk-{chunk_id}",
                        "text": chunk_text,
                        "source": file_name,
                        "chunk_id": chunk_id,
                    }
                    documents.append(doc)
        
        # Load PDF files (if available)
        for file_path in data_dir.rglob("*.pdf" if recursive else "*.pdf"):
            if file_path.is_file():
                logger.info(f"Processing PDF: {file_path.name}")
                chunks = self.processor.load_pdf_file(
                    file_path,
                    max_chars=self.config.chunk_size
                )
                
                for chunk_text, chunk_id, file_name in chunks:
                    doc = {
                        "id": f"{file_name}::chunk-{chunk_id}",
                        "text": chunk_text,
                        "source": file_name,
                        "chunk_id": chunk_id,
                    }
                    documents.append(doc)
        
        if not documents:
            logger.warning(f"No documents found in {data_dir}")
            return 0
        
        # Index documents
        logger.info(f"Indexing {len(documents)} document chunks...")
        indexed_count = self.search_engine.index_documents(documents)
        
        logger.info(f"Successfully indexed {indexed_count} documents")
        return indexed_count
    
    def index_custom_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Index custom documents."""
        logger.info(f"Indexing {len(documents)} custom documents...")
        
        # Validate documents
        for doc in documents:
            if "id" not in doc or "text" not in doc:
                raise ValueError("Each document must have 'id' and 'text' fields")
        
        # Index documents
        indexed_count = self.search_engine.index_documents(documents)
        
        logger.info(f"Successfully indexed {indexed_count} documents")
        return indexed_count
    
    def add_document(self, doc_id: str, text: str, source: str = "custom") -> bool:
        """Add a single document."""
        document = {
            "id": doc_id,
            "text": text,
            "source": source,
            "chunk_id": 0,
        }
        
        try:
            self.search_engine.index_documents([document])
            logger.info(f"Added document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def clear_index(self) -> bool:
        """Clear all indexed documents."""
        try:
            self.search_engine.vector_store.clear_index()
            logger.info("Index cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False
