#!/usr/bin/env bash
# Quick start script for development

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"

echo "=========================================="
echo "AI Research Assistant - Quick Start"
echo "=========================================="
echo

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "✗ Python 3 not found"; exit 1; }
echo

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "✓ Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt
echo

# Create data directory
mkdir -p data logs
echo "✓ Created data and logs directories"
echo

# Show configuration
echo "=========================================="
echo "Configuration"
echo "=========================================="
echo "Edit .env to customize settings"
echo
cp .env.example .env 2>/dev/null || true
echo

# Show next steps
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo "1. Start Endee vector database:"
echo "   ./run.sh  (or docker-compose up)"
echo
echo "2. Index documents:"
echo "   python main.py index --source data"
echo
echo "3. Ask questions:"
echo "   python main.py query 'Your question here?'"
echo
echo "4. Interactive chat:"
echo "   python main.py chat"
echo
echo "=========================================="
echo
echo "✓ Setup complete!"
