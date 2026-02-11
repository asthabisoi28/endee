"""Semantic search and retrieval components using Endee."""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from endee import Endee, Precision
from sentence_transformers import SentenceTransformer

from config import AppConfig, EndeeConfig, EmbeddingConfig
from utils import EmbeddingCache, logger


@dataclass
class RetrievedDocument:
    """A document retrieved from the vector database."""
    id: str
    text: str
    source: str
    chunk_id: int
    similarity: float
    metadata: Dict[str, Any]


class EmbeddingModel:
    """Wrapper for embedding model with caching."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.model = None
        self.cache = EmbeddingCache()
        logger.info(f"Loading embedding model: {config.model_name}")
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            self.model = SentenceTransformer(
                self.config.model_name,
                device=self.config.device
            )
            logger.info(f"Embedding model loaded. Device: {self.config.device}")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts."""
        self._load_model()
        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings.tolist()
    
    def embed_single(self, text: str) -> List[float]:
        """Embed a single text with caching."""
        # Check cache
        cached = self.cache.get(text)
        if cached:
            logger.debug("Using cached embedding")
            return cached
        
        # Compute and cache
        self._load_model()
        embedding = self.model.encode(
            [text],
            convert_to_numpy=True,
            show_progress_bar=False
        ).tolist()[0]
        
        self.cache.set(text, embedding)
        return embedding


class VectorStore:
    """Interface to Endee vector database."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = None
        self.index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Endee client and index."""
        try:
            self.client = Endee(token=self.config.endee.token)
            if self.config.endee.base_url:
                self.client.set_base_url(self.config.endee.base_url)
            logger.info(f"Connected to Endee at {self.config.endee.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Endee: {e}")
            raise
    
    def ensure_index(self) -> None:
        """Create index if it doesn't exist."""
        try:
            existing = self.client.list_indexes()
            existing_names = set()
            
            for idx in existing or []:
                if isinstance(idx, str):
                    existing_names.add(idx)
                elif isinstance(idx, dict):
                    name = idx.get("name") or idx.get("index_name")
                    if name:
                        existing_names.add(name)
            
            if self.config.endee.index_name not in existing_names:
                logger.info(
                    f"Creating index '{self.config.endee.index_name}' "
                    f"(dim={self.config.endee.vector_dim}, "
                    f"space={self.config.endee.space_type})"
                )
                self.client.create_index(
                    name=self.config.endee.index_name,
                    dimension=self.config.endee.vector_dim,
                    space_type=self.config.endee.space_type,
                    precision=Precision.INT8D,
                )
            else:
                logger.info(f"Using existing index '{self.config.endee.index_name}'")
            
            self.index = self.client.get_index(name=self.config.endee.index_name)
        except Exception as e:
            logger.error(f"Failed to ensure index: {e}")
            raise
    
    def upsert(self, documents: List[Dict[str, Any]]) -> None:
        """Upsert documents into the vector store."""
        if self.index is None:
            self.ensure_index()
        
        try:
            batch_size = 256
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                self.index.upsert(batch)
                logger.info(f"Upserted batch {i//batch_size + 1} ({len(batch)} documents)")
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            raise
    
    def search(
        self,
        vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """Search the vector store."""
        if self.index is None:
            self.ensure_index()
        
        try:
            results = self.index.query(vector=vector, top_k=top_k)
            
            documents = []
            for item in results or []:
                meta = item.get("meta", {}) or {}
                doc = RetrievedDocument(
                    id=item.get("id", ""),
                    text=meta.get("text", ""),
                    source=meta.get("source", ""),
                    chunk_id=meta.get("chunk_id", 0),
                    similarity=float(item.get("similarity", 0.0)),
                    metadata=meta
                )
                documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def clear_index(self) -> None:
        """Delete the current index."""
        try:
            self.client.delete_index(name=self.config.endee.index_name)
            logger.info(f"Deleted index '{self.config.endee.index_name}'")
            self.index = None
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            raise


class SemanticSearchEngine:
    """High-level semantic search interface."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.embedding_model = EmbeddingModel(config.embedding)
        self.vector_store = VectorStore(config)
        self.vector_store.ensure_index()
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Index documents with embeddings."""
        logger.info(f"Indexing {len(documents)} documents...")
        
        # Extract texts for embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.embed(texts)
        
        # Prepare documents for upsert
        docs_to_upsert = []
        for doc, embedding in zip(documents, embeddings):
            doc_with_embedding = {
                "id": doc["id"],
                "vector": embedding,
                "meta": {
                    "text": doc["text"],
                    "source": doc.get("source", "unknown"),
                    "chunk_id": doc.get("chunk_id", 0),
                },
                "filter": {
                    "source": doc.get("source", "unknown"),
                }
            }
            docs_to_upsert.append(doc_with_embedding)
        
        # Upsert to vector store
        self.vector_store.upsert(docs_to_upsert)
        logger.info(f"Successfully indexed {len(documents)} documents")
        
        return len(documents)
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[RetrievedDocument]:
        """Perform semantic search."""
        top_k = top_k or self.config.top_k
        min_similarity = min_similarity or self.config.similarity_threshold
        
        logger.info(f"Searching: {query}")
        
        # Embed query
        query_embedding = self.embedding_model.embed_single(query)
        
        # Search
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Filter by similarity
        filtered_results = [
            doc for doc in results
            if doc.similarity >= min_similarity
        ]
        
        logger.info(f"Found {len(filtered_results)}/{len(results)} relevant results")
        
        return filtered_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed documents."""
        # This would require additional Endee API support
        return {
            "index_name": self.config.endee.index_name,
            "embedding_model": self.config.embedding.model_name,
            "vector_dim": self.config.endee.vector_dim,
        }
