# AI Research Assistant - Powered by Endee Vector Database

A production-ready AI/ML application demonstrating semantic search, retrieval-augmented generation (RAG), and agentic AI workflows using [Endee](https://github.com/endee/endee) as the vector database.

## Features

✨ **Core Capabilities**
- **Semantic Search**: Find relevant documents using vector embeddings
- **Question Answering**: Get intelligent answers with citations from your knowledge base
- **Document Indexing**: Support for TXT, Markdown, and PDF files
- **Interactive Chat**: Multi-turn conversation with context awareness
- **Batch Processing**: Process multiple queries efficiently
- **Confidence Scoring**: Understand answer reliability based on source quality

🚀 **Production-Ready**
- Modular architecture with clear separation of concerns
- Comprehensive error handling and logging
- Configuration management for all components
- Efficient embedding caching
- Batch processing for better performance

🔧 **Technology Stack**
- **Vector Database**: [Endee](https://github.com/endee/endee) - High-performance vector search
- **Embeddings**: [Sentence-Transformers](https://www.sbert.net/) - State-of-the-art text embeddings
- **LLM Integration**: OpenAI, Anthropic, or local models
- **Framework**: Click CLI framework
- **Configuration**: Environment-based configuration

## Quick Start

### Prerequisites

- Python 3.9+
- Endee vector database running (see [Endee documentation](https://github.com/endee/endee) for setup)
- Optional: OpenAI API key for advanced QA features

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/endee-research-assistant.git
   cd endee-research-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** (optional, for custom configuration)
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your settings:
   ```env
   # Endee Configuration
   ENDEE_BASE_URL=http://localhost:8080/api/v1
   ENDEE_INDEX_NAME=research_assistant
   VECTOR_DIM=384

   # Embedding Model
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DEVICE=cpu  # or cuda, mps

   # LLM Configuration
   LLM_PROVIDER=openai  # or anthropic, ollama
   LLM_MODEL=gpt-3.5-turbo
   LLM_API_KEY=your_api_key_here

   # Retrieval Settings
   TOP_K=5
   SIMILARITY_THRESHOLD=0.3
   ```

### Running Endee

Before using the application, start the Endee vector database:

```bash
# Using the provided run.sh script
./run.sh

# Or with docker
docker-compose up -d
```

Endee will be available at `http://localhost:8080/api/v1`

### Usage

#### 1. Index Documents

Place your documents in the `data/` directory (supports `.txt`, `.md`, `.pdf`), then index them:

```bash
python main.py index --source data
```

Or with directory auto-creation:
```bash
python main.py index
```

Clear existing index before re-indexing:
```bash
python main.py index --clear
```

#### 2. Query the Knowledge Base

Single query:
```bash
python main.py query "What is semantic search?"
```

With options:
```bash
python main.py query "How does vector search work?" --top-k 10 --json
```

#### 3. Interactive Chat

Start an interactive conversation:
```bash
python main.py chat
```

Commands:
- Type questions normally
- `quit` - Exit the chat
- `clear` - Clear conversation history

#### 4. Batch Processing

Process multiple queries from the command line:
```bash
python main.py batch --queries "Question 1?" "Question 2?" "Question 3?"
```

Or from a file (one question per line):
```bash
python main.py batch --file queries.txt --output results.json
```

#### 5. View System Information

```bash
python main.py info
```

#### 6. Manage Index

Clear the index:
```bash
python main.py clear
```

## Project Structure

```
endee-research-assistant/
├── main.py                 # CLI application entry point
├── config.py              # Configuration management
├── utils.py               # Utility functions (logging, text processing)
├── retriever.py           # Semantic search engine
├── qa_agent.py            # Question answering agent
├── indexer.py             # Document indexing pipeline
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment configuration
├── data/                  # Document storage (auto-created)
│   ├── sample.md
│   └── ...
├── logs/                  # Application logs (auto-created)
└── README.md              # This file
```

### Module Overview

**config.py**
- Configuration management for Endee, embeddings, and LLMs
- Environment variable loading
- Type-safe dataclass-based config

**utils.py**
- Document processing (text, PDF, markdown)
- Text cleaning and truncation
- Embedding caching for performance
- Logging setup

**retriever.py**
- `EmbeddingModel`: Wrapper for Sentence-Transformers with caching
- `VectorStore`: Interface to Endee vector database
- `SemanticSearchEngine`: High-level semantic search API

**qa_agent.py**
- `LLMInterface`: Abstract LLM interface
- `OpenAIInterface`: OpenAI API implementation
- `ResearchAssistantAgent`: Main agent for QA and retrieval
- Interactive chat and batch processing capabilities

**indexer.py**
- `DocumentIndexer`: Manages document indexing pipeline
- Directory scanning and file processing
- Batch indexing with progress tracking

## Example Use Cases

### 1. Technical Documentation Search

```bash
# Index your technical documentation
python main.py index --source ./tech-docs

# Ask questions about it
python main.py query "How do I configure authentication?"
```

### 2. Knowledge Base Q&A

```bash
# Build a knowledge base from multiple sources
cp /path/to/documents/* ./data/
python main.py index

# Interactive research session
python main.py chat
```

### 3. Research Paper Analysis

```bash
# Add PDF papers to data/
python main.py index

# Batch analyze with specific questions
python main.py batch --queries \
  "What novel techniques are introduced?" \
  "How does this compare to prior work?" \
  "What are the main limitations?"
```

## Configuration

The application uses environment variables for configuration. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENDEE_BASE_URL` | `http://localhost:8080/api/v1` | Endee server URL |
| `ENDEE_INDEX_NAME` | `research_assistant` | Vector index name |
| `VECTOR_DIM` | `384` | Embedding dimension |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-Transformers model |
| `EMBEDDING_DEVICE` | `cpu` | Device for embeddings (cpu/cuda/mps) |
| `LLM_PROVIDER` | `openai` | LLM provider (openai/anthropic) |
| `LLM_MODEL` | `gpt-3.5-turbo` | LLM model name |
| `LLM_API_KEY` | - | API key for LLM provider |
| `TOP_K` | `5` | Number of documents to retrieve |
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum similarity score |
| `CHUNK_SIZE` | `800` | Document chunk size in characters |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `DEBUG` | `false` | Enable debug logging |

## Performance Optimization

### Embedding Caching
The application automatically caches embeddings to avoid redundant computations:

```python
# Second query for identical text will use cache
result1 = agent.answer_question("What is AI?")
result2 = agent.answer_question("What is AI?")  # Uses cached embedding
```

### Batch Processing
Use batch mode for processing many queries efficiently:

```bash
python main.py batch --file 1000_questions.txt --output results.json
```

### Tuning Parameters

**For Better Recall:**
- Decrease `SIMILARITY_THRESHOLD`
- Increase `TOP_K`
- Increase `CHUNK_SIZE`

**For Better Precision:**
- Increase `SIMILARITY_THRESHOLD`
- Decrease `TOP_K`
- Decrease `CHUNK_SIZE`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (CLI/Chat)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              ResearchAssistantAgent (qa_agent.py)           │
│           ┌──────────────────────────────────┐              │
│           │ Answer Question / Chat / Batch   │              │
│           └──────────────────────────────────┘              │
└────┬─────────────────────────────────────────┬──────────────┘
     │                                         │
┌────▼──────────────────┐      ┌──────────────▼─────────┐
│ SemanticSearchEngine  │      │   LLMInterface         │
│  (retriever.py)       │      │  (qa_agent.py)         │
│                       │      │                        │
│  • EmbeddingModel     │      │  • OpenAI             │
│  • VectorStore        │      │  • Anthropic          │
│  • Search             │      │  • Local/Fallback     │
└────┬──────────────────┘      └──────────────────────┘
     │
┌────▼──────────────────────────────────────────────────────┐
│         Endee Vector Database (HTTP API)                  │
│      http://localhost:8080/api/v1                         │
└───────────────────────────────────────────────────────────┘
```

## API Reference

### Core Classes

#### `SemanticSearchEngine`
```python
engine = SemanticSearchEngine(config)

# Index documents
indexed = engine.index_documents([
    {"id": "doc1", "text": "Document content", "source": "file.md", "chunk_id": 0}
])

# Search
results = engine.search("query", top_k=5, min_similarity=0.3)
# Returns: List[RetrievedDocument]
```

#### `ResearchAssistantAgent`
```python
agent = ResearchAssistantAgent(config)

# Answer a single question
result = agent.answer_question("What is AI?", top_k=5)
# Returns: QAResult with answer, sources, confidence

# Batch answers
results = agent.batch_answer(["Q1?", "Q2?", "Q3?"])

# Interactive chat
agent.interactive_chat()
```

#### `DocumentIndexer`
```python
indexer = DocumentIndexer(config)

# Index a directory
count = indexer.index_directory(Path("./data"))

# Index custom documents
indexer.index_custom_documents([
    {"id": "doc1", "text": "content", "source": "custom"}
])

# Add single document
indexer.add_document("doc_id", "content", "source")

# Clear index
indexer.clear_index()
```

## Troubleshooting

### Connection Issues

**Error: "Failed to connect to Endee"**
- Ensure Endee is running: `./run.sh` or `docker-compose up`
- Check `ENDEE_BASE_URL` in `.env`
- Verify network connectivity: `curl http://localhost:8080/api/v1/indexes`

### Embedding Issues

**Error: "Embedding model not found"**
- First run downloads the model from HuggingFace
- Requires internet connection
- Model cache location: `~/.cache/huggingface/`

**Slow embeddings?**
- Use GPU: Set `EMBEDDING_DEVICE=cuda` (requires CUDA/PyTorch)
- Reduce batch size: `EMBEDDING_BATCH_SIZE=16`
- Use smaller model: `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`

### LLM Issues

**Error: "API key not configured"**
- Set `LLM_API_KEY` in `.env`
- Or set environment variable: `export LLM_API_KEY=your_key`

**Using fallback responses?**
- Check `LLM_PROVIDER` setting
- Ensure API keys are valid
- Check logs in `logs/` directory

### No Search Results

- Ensure documents are indexed: `python main.py index`
- Check similarity threshold: Decrease `SIMILARITY_THRESHOLD`
- Verify Endee is running and has indexed documents
- Check logs for errors

## Advanced Usage

### Custom Embedding Model

```python
from config import load_config
from retriever import EmbeddingModel

config = load_config()
config.embedding.model_name = "sentence-transformers/all-mpnet-base-v2"

model = EmbeddingModel(config.embedding)
embeddings = model.embed(["text1", "text2"])
```

### Custom LLM Integration

```python
from qa_agent import LLMInterface, ResearchAssistantAgent

class MyLLMInterface(LLMInterface):
    def generate(self, prompt: str, context: str = "") -> str:
        # Custom LLM logic here
        return "Custom response"

agent = ResearchAssistantAgent(config)
agent.llm = MyLLMInterface(config.llm)
```

### Programmatic Usage

```python
from config import load_config, setup_logging
from qa_agent import ResearchAssistantAgent
from indexer import DocumentIndexer

# Setup
config = load_config()
logger = setup_logging(config)

# Index documents
indexer = DocumentIndexer(config)
indexer.index_directory()

# Ask questions
agent = ResearchAssistantAgent(config)
result = agent.answer_question("What is semantic search?")

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence:.2%}")
for source in result.sources:
    print(f"  - {source['source']}")
```

## Contributing

Contributions welcome! Areas for enhancement:

- [ ] Support for more document types (DOCX, HTML, JSON)
- [ ] Multi-language support
- [ ] Advanced filtering and metadata support
- [ ] Performance benchmarking suite
- [ ] Web UI for document management
- [ ] Integration with more LLM providers
- [ ] Streaming responses for long-form QA

## License

MIT License - see LICENSE file for details

## Citation

If you use this project in your research, please cite:

```bibtex
@software{endee_research_assistant,
  title={AI Research Assistant - Powered by Endee},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/endee-research-assistant}
}
```

## Acknowledgments

### Built With
- [Endee](https://github.com/endee/endee) - High-performance vector database
- [Sentence-Transformers](https://www.sbert.net/) - State-of-the-art embeddings
- [OpenAI](https://openai.com) - LLM capabilities
- [Click](https://click.palletsprojects.com/) - CLI framework

## Resources

- [Endee Documentation](https://github.com/endee/endee)
- [Sentence-Transformers](https://www.sbert.net/)
- [Vector Search Guide](https://www.pinecone.io/learn/vector-search/)
- [RAG with LLMs](https://arxiv.org/abs/2005.11401)

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review logs in `logs/` directory for troubleshooting

---

**Last Updated**: February 11, 2026

Happy researching! 🚀
