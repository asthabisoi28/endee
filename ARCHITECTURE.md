# Project Structure Documentation

## Directory Overview

```
endee-research-assistant/
├── .env.example                      # Example environment configuration
├── .github/
│   └── workflows/
│       ├── tests.yml                # Automated testing workflow
│       └── docker.yml               # Docker build and push workflow
├── .gitignore                        # Git ignore rules
├── CHANGELOG.md                      # Version history and changes
├── CONTRIBUTING.md                  # Contribution guidelines
├── Dockerfile                        # Docker container definition
├── EXAMPLES.md                       # Usage examples and patterns
├── GITHUB_SETUP.md                  # GitHub hosting instructions
├── LICENSE                          # MIT License
├── README.md                         # Main documentation
├── QUICKSTART.sh                    # Quick start setup script
├── config.py                        # Configuration management
├── docker-compose.yml               # Multi-service Docker setup
├── indexer.py                       # Document indexing pipeline
├── main.py                          # CLI application entry point
├── qa_agent.py                      # Question answering agent
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
├── retriever.py                     # Semantic search engine
├── setup.sh                         # Unix setup script
├── utils.py                         # Utility functions
├── data/                            # Document storage
│   ├── README.md                    # Data directory guide
│   ├── rag-guide.md                # RAG documentation
│   └── vector-databases.md         # Vector DB documentation
├── logs/                            # Application logs (auto-created)
└── tests/                           # Test suite
    └── test_basic.py               # Basic tests
```

## Core Modules

### config.py
Configuration management with dataclass-based approach.

**Key Components:**
- `EndeeConfig` - Vector database configuration
- `EmbeddingConfig` - Embedding model settings
- `LLMConfig` - Language model configuration
- `AppConfig` - Main application configuration
- `load_config()` - Load from environment variables

**Usage:**
```python
from config import load_config, setup_logging

config = load_config()
logger = setup_logging(config)
```

### utils.py
Utility functions for document processing and logging.

**Key Classes:**
- `DocumentProcessor` - Load and chunk documents
- `EmbeddingCache` - Cache embeddings to avoid recomputation
- `TextCleaner` - Normalize and format text

**Usage:**
```python
from utils import DocumentProcessor, logger

processor = DocumentProcessor()
chunks = processor.load_text_file(Path("document.txt"))
```

### retriever.py
Semantic search engine based on embeddings and Endee.

**Key Classes:**
- `EmbeddingModel` - Wrapper for Sentence-Transformers
- `VectorStore` - Interface to Endee database
- `SemanticSearchEngine` - High-level search API
- `RetrievedDocument` - Retrieved document data structure

**Usage:**
```python
from retriever import SemanticSearchEngine

engine = SemanticSearchEngine(config)
documents = engine.index_documents(docs)
results = engine.search("query", top_k=5)
```

### qa_agent.py
Question answering with LLM integration.

**Key Classes:**
- `LLMInterface` - Abstract LLM interface
- `OpenAIInterface` - OpenAI API implementation
- `ResearchAssistantAgent` - Main QA agent
- `QAResult` - Question answering result

**Usage:**
```python
from qa_agent import ResearchAssistantAgent

agent = ResearchAssistantAgent(config)
result = agent.answer_question("Your question?")
print(result.answer)
```

### indexer.py
Document indexing pipeline.

**Key Classes:**
- `DocumentIndexer` - Index documents from directory or custom list

**Usage:**
```python
from indexer import DocumentIndexer

indexer = DocumentIndexer(config)
count = indexer.index_directory(Path("data"))
```

### main.py
Command-line interface using Click framework.

**Available Commands:**
- `index` - Index documents
- `query` - Ask a single question
- `chat` - Interactive conversation
- `batch` - Process multiple queries
- `info` - Show system information
- `clear` - Delete index

**Usage:**
```bash
python main.py index
python main.py query "Question?"
python main.py chat
```

## File Purposes

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation and usage guide |
| `.env.example` | Template for environment configuration |
| `Dockerfile` | Docker container specification |
| `docker-compose.yml` | Multi-service orchestration |
| `.github/workflows/` | CI/CD automation |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development dependencies |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CHANGELOG.md` | Version history |
| `EXAMPLES.md` | Code examples and patterns |
| `GITHUB_SETUP.md` | GitHub repository setup guide |
| `QUICKSTART.sh` | Quick installation script |
| `tests/` | Test suite |

## Data Flow

```
User Input (CLI/Chat)
        ↓
main.py (CLI Handler)
        ↓
    {
    index: DocumentIndexer → Indexer → SemanticSearchEngine
    query: QueryProcessor → SemanticSearchEngine → ResearchAssistantAgent → LLM
    chat: ChatInterface → ResearchAssistantAgent → LLM
    }
        ↓
Output (Answer with Sources)
```

## Architecture Layers

```
┌─────────────────────────────────────────┐
│     User Interface (CLI/Chat)           │
├─────────────────────────────────────────┤
│     Application Layer (main.py)         │
├─────────────────────────────────────────┤
│     Business Logic Layer                │
│  ┌──────────────────┬────────────────┐  │
│  │ ResearchAssistant│ DocumentIndexer│  │
│  └────────┬─────────┴────────┬───────┘  │
├──────────┼──────────────────┼──────────┤
│     Integration Layer                   │
│  ┌──────────────────┬────────────────┐  │
│  │ SemanticSearch   │    LLMInterface│  │
│  └────────┬─────────┴────────┬───────┘  │
├──────────┼──────────────────┼──────────┤
│     Infrastructure Layer                │
│  ┌──────────────┬────────────┬────────┐ │
│  │ EmbeddingModel│ VectorStore│Utilities│ │
│  └──────────────┴────────────┴────────┘ │
├─────────────────────────────────────────┤
│  External Services                      │
│  ┌────────────┬─────────┬──────────────┐ │
│  │Endee Vector│ Sentence│ LLM Provider │ │
│  │ Database   │Transform│ (OpenAI etc.)│ │
│  └────────────┴─────────┴──────────────┘ │
└─────────────────────────────────────────┘
```

## Configuration Hierarchy

1. **Default Values** (in code)
   - Built-in reasonable defaults
   - Model names, batch sizes, etc.

2. **Environment Variables**
   - Override defaults
   - Loaded from `.env` file
   - System environment variables

3. **Programmatic Override**
   - Direct code configuration
   - Useful for testing and custom deployments

## Error Handling Strategy

1. **Logging** - All errors logged with context
2. **User Feedback** - Clear error messages in CLI
3. **Graceful Degradation** - Fall back to simpler responses
4. **Validation** - Input validation at entry points
5. **Retry Logic** - Automatic retries for API calls

## Performance Considerations

| Component | Optimization |
|-----------|--------------|
| Embeddings | Cached, batched inference |
| Vector Search | HNSW indexing (Endee) |
| LLM Calls | Configurable token limits |
| Memory | Optional quantization (INT8D) |
| Disk | Logs auto-rotation recommended |

## Testing Strategy

- **Unit Tests** - Individual component functionality
- **Integration Tests** - Component interactions
- **E2E Tests** - Full workflow testing
- **Mock Services** - Simulate Endee/LLM for testing

## Development Workflow

1. Create feature branch
2. Modify code
3. Run tests
4. Update documentation
5. Commit with clear message
6. Create pull request
7. Code review
8. Merge to main
9. Tag release

## Deployment Checklist

- [ ] All tests passing
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] Environment variables documented
- [ ] Dependencies pinned
- [ ] Docker image tested
- [ ] GitHub Actions workflows passing
- [ ] Performance benchmarks acceptable
- [ ] Security review completed
- [ ] Release notes prepared
