"""
Usage Examples for AI Research Assistant

This module demonstrates various ways to use the AI Research Assistant
programmatically in your own projects.
"""

# Example 1: Basic Question Answering
# ====================================

from config import load_config, setup_logging
from qa_agent import ResearchAssistantAgent
from indexer import DocumentIndexer

# Load configuration
config = load_config()
logger = setup_logging(config)

# Create indexer and index documents
indexer = DocumentIndexer(config)
indexer.index_directory()  # Index all documents in data/

# Create agent and ask a question
agent = ResearchAssistantAgent(config)
result = agent.answer_question("What is semantic search?")

print(f"Q: {result.question}")
print(f"A: {result.answer}")
print(f"Confidence: {result.confidence:.2%}")


# Example 2: Semantic Search Without LLM
# ========================================

from retriever import SemanticSearchEngine

# Create search engine
search_engine = SemanticSearchEngine(config)

# Search for relevant documents
results = search_engine.search("vector databases", top_k=5)

# Process results
for doc in results:
    print(f"Source: {doc.source}")
    print(f"Similarity: {doc.similarity:.4f}")
    print(f"Content: {doc.text[:200]}...")
    print()


# Example 3: Custom Document Indexing
# ====================================

from datetime import datetime

documents = [
    {
        "id": "doc_001",
        "text": "Machine learning is a subset of AI that enables systems to learn from data.",
        "source": "ai_glossary.txt",
        "chunk_id": 0,
    },
    {
        "id": "doc_002",
        "text": "Deep learning uses neural networks with multiple layers for representation learning.",
        "source": "ai_glossary.txt",
        "chunk_id": 1,
    },
    {
        "id": "doc_003",
        "text": "Natural Language Processing deals with text understanding and generation.",
        "source": "ai_glossary.txt",
        "chunk_id": 2,
    },
]

indexer = DocumentIndexer(config)
indexed_count = indexer.index_custom_documents(documents)
print(f"Indexed {indexed_count} documents")


# Example 4: Batch Processing Queries
# ====================================

questions = [
    "What is machine learning?",
    "Explain deep learning",
    "What is NLP?",
    "How do embeddings work?",
]

agent = ResearchAssistantAgent(config)
results = agent.batch_answer(questions)

for result in results:
    print(f"Q: {result.question}")
    print(f"A: {result.answer[:200]}...")
    print()


# Example 5: Interactive Chat Session
# ====================================

agent = ResearchAssistantAgent(config)
agent.interactive_chat()


# Example 6: Filter and Search with Metadata
# ===========================================

# You can add metadata filters when retrieving
search_engine = SemanticSearchEngine(config)

# Search with document filtering
results = search_engine.search(
    "How do embeddings work?",
    top_k=3,
    min_similarity=0.4
)

for doc in results:
    print(f"File: {doc.source}")
    print(f"Chunk: {doc.chunk_id}")
    print(f"Similarity Score: {doc.similarity}")


# Example 7: Building a Search API
# =================================

from typing import List, Dict, Any

class SearchAPI:
    """Simple API wrapper around the search engine."""
    
    def __init__(self, config):
        self.agent = ResearchAssistantAgent(config)
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform a search and return structured results."""
        results = self.agent.search_engine.search(query, top_k=top_k)
        
        return {
            "query": query,
            "results": [
                {
                    "id": doc.id,
                    "text": doc.text,
                    "source": doc.source,
                    "similarity": doc.similarity,
                }
                for doc in results
            ],
            "count": len(results),
        }
    
    def answer(self, question: str) -> Dict[str, Any]:
        """Answer a question with sources."""
        result = self.agent.answer_question(question)
        
        return {
            "question": question,
            "answer": result.answer,
            "confidence": result.confidence,
            "sources": result.sources,
        }

# Usage
api = SearchAPI(config)

search_result = api.search("machine learning")
print(search_result)

qa_result = api.answer("What is machine learning?")
print(qa_result)


# Example 8: Flask Web Service
# ============================

from flask import Flask, request, jsonify

app = Flask(__name__)
api = SearchAPI(load_config())

@app.route("/search", methods=["POST"])
def search():
    """Search endpoint."""
    data = request.json
    query = data.get("query", "")
    top_k = data.get("top_k", 5)
    
    result = api.search(query, top_k=top_k)
    return jsonify(result)

@app.route("/qa", methods=["POST"])
def qa():
    """Question answering endpoint."""
    data = request.json
    question = data.get("question", "")
    
    result = api.answer(question)
    return jsonify(result)

# Run: flask run


# Example 9: Configuration for Different Scenarios
# ==================================================

# Use smaller, faster model for latency-sensitive scenarios
config.embedding.model_name = "sentence-transformers/all-MiniLM-L6-v2"
config.embedding.batch_size = 8

# Use larger, more accurate model for offline processing
config.embedding.model_name = "sentence-transformers/all-mpnet-base-v2"
config.embedding.batch_size = 64

# Configure for GPU
config.embedding.device = "cuda"

# Configure for production with high accuracy
config.similarity_threshold = 0.5
config.top_k = 10


# Example 10: Error Handling
# ===========================

try:
    agent = ResearchAssistantAgent(config)
    result = agent.answer_question("Complex question?")
    
    if result.confidence < 0.3:
        print("Low confidence answer - user should verify results")
    else:
        print(result.answer)
        
except Exception as e:
    logger.error(f"Error processing question: {e}")
    print("Failed to process question")


# Example 11: Logging and Monitoring
# ===================================

import logging
from config import setup_logging

# Enable debug logging
config.debug = True
logger = setup_logging(config)

# Log important events
logger.info("Indexing started")
indexer = DocumentIndexer(config)
count = indexer.index_directory()
logger.info(f"Indexed {count} documents")

logger.info("Starting Q&A session")
agent = ResearchAssistantAgent(config)
result = agent.answer_question("Sample question?")

if result.confidence > 0.7:
    logger.info(f"High confidence answer: {result.answer[:100]}")
else:
    logger.warning(f"Low confidence answer: {result.answer[:100]}")
