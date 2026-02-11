# Sample Documents for Testing

This directory contains sample documents for indexing and searching. You can add your own documents here.

## Supported File Types

- **Text Files** (`.txt`) - Plain text documents
- **Markdown** (`.md`) - Markdown formatted documents
- **PDF** (`.pdf`) - PDF documents (requires PyPDF2)

## Adding Documents

1. Create a file in this directory with one of the supported extensions
2. Run: `python main.py index --source data`
3. Query with: `python main.py query "your question"`

## Example

```bash
# Add a document
echo "Vector databases are specialized database systems optimized for storing and searching high-dimensional vectors." > data/vectors.txt

# Index it
python main.py index

# Search
python main.py query "What is a vector database?"
```

## Structure

For best results, organize your documents:

```
data/
├── technical/
│   ├── vectors.md
│   └── embeddings.md
├── research/
│   ├── paper1.pdf
│   └── paper2.pdf
└── general/
    ├── guide.txt
    └── tutorial.md
```
