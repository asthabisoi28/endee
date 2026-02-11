#!/usr/bin/env bash

# Quick Start Guide - AI Research Assistant

set -e

echo "════════════════════════════════════════════════════════════════"
echo "         AI Research Assistant - Quick Start Guide"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo "→ $1"
    echo ""
}

# Check Prerequisites
print_section "Checking Prerequisites"

if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required but not installed"
    exit 1
fi
echo "✓ Python $(python3 --version 2>&1 | cut -d' ' -f2)"

if ! command -v git &> /dev/null; then
    echo "✗ Git is required but not installed"
    exit 1
fi
echo "✓ Git installed"

# Clone or Install
print_section "Step 1: Get the Project"

if [ ! -d ".git" ]; then
    echo "Clone from GitHub (if not already done)"
    # git clone https://github.com/yourusername/endee-research-assistant.git
    # cd endee-research-assistant
    echo "Project already initialized"
else
    echo "✓ Project directory ready"
fi

# Create Virtual Environment
print_section "Step 2: Set Up Python Environment"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate Virtual Environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
echo "✓ Virtual environment activated"

# Install Dependencies
print_section "Step 3: Install Dependencies"

echo "Installing Python packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Configuration
print_section "Step 4: Configure Application"

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ Configuration file created"
    echo ""
    echo "   Edit .env to customize settings"
    echo "   Key settings:"
    echo "   - ENDEE_BASE_URL: http://localhost:8080/api/v1"
    echo "   - LLM_PROVIDER: openai (or anthropic, local)"
    echo "   - LLM_API_KEY: your API key here"
else
    echo "✓ .env already configured"
fi

# Create Directories
print_section "Step 5: Set Up Data Directories"

mkdir -p data logs
echo "✓ Created data/ and logs/ directories"

# Show System Info
print_section "Step 6: Verify Installation"

python3 main.py info

# Start Guide
print_section "Quick Start Commands"

echo "1. Check if Endee is running (in another terminal):"
echo "   → ./run.sh"
echo "   → docker-compose up"
echo ""
echo "2. Index your documents:"
echo "   → python3 main.py index"
echo ""
echo "3. Ask questions:"
echo "   → python3 main.py query 'What is semantic search?'"
echo ""
echo "4. Start interactive chat:"
echo "   → python3 main.py chat"
echo ""
echo "5. Process multiple queries:"
echo "   → python3 main.py batch --queries 'Q1?' 'Q2?' 'Q3?'"
echo ""

# Final Steps
print_section "Next Steps"

echo "1. Start Endee vector database:"
echo "   • Download from: https://github.com/endee/endee"
echo "   • Or use: docker-compose up"
echo ""
echo "2. Add documents to data/ folder:"
echo "   • Supported: .txt, .md, .pdf"
echo "   • Example files already in data/ folder"
echo ""
echo "3. Configure API keys (.env):"
echo "   • For OpenAI: https://platform.openai.com/api-keys"
echo "   • For Anthropic: https://console.anthropic.com/"
echo ""

# Complete
print_section "Installation Complete! ✓"

echo "You're ready to use the AI Research Assistant!"
echo ""
echo "For help:"
echo "   → python3 main.py --help"
echo "   → Read README.md for detailed documentation"
echo ""
echo "════════════════════════════════════════════════════════════════"
