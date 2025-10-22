#!/bin/bash
# AI Router Setup Script
# Purpose: Initialize AI Router development environment
# Created: 2025-10-22

set -e  # Exit on error

echo "==================================="
echo "AI Router Setup Script"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Task T010: Install Python dependencies
echo "Task T010: Installing Python dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for faster installation..."
    uv pip install -r requirements-ai-router.txt
else
    echo "Using pip..."
    pip install -r requirements-ai-router.txt
fi
echo "✓ Dependencies installed"
echo ""

# Task T011: Run PostgreSQL migration
echo "Task T011: Running PostgreSQL migration..."
echo "Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    if [ -z "$POSTGRES_HOST" ]; then
        export POSTGRES_HOST=localhost
    fi
    if [ -z "$POSTGRES_USER" ]; then
        export POSTGRES_USER=postgres
    fi
    if [ -z "$POSTGRES_DB" ]; then
        export POSTGRES_DB=recruitment
    fi

    echo "Running migration on $POSTGRES_HOST/$POSTGRES_DB..."
    psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f sql/migrations/001_create_routing_logs.sql
    echo "✓ Database migration completed"
else
    echo "⚠ psql not found. Please install PostgreSQL client or run migration manually:"
    echo "  psql -h localhost -U postgres -d recruitment -f sql/migrations/001_create_routing_logs.sql"
fi
echo ""

# Task T012: Verify Redis connection
echo "Task T012: Verifying Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping | grep -q "PONG"; then
        echo "✓ Redis connection successful"
    else
        echo "⚠ Redis not responding. Please start Redis server:"
        echo "  redis-server"
    fi
else
    echo "⚠ redis-cli not found. Please install Redis:"
    echo "  - Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  - macOS: brew install redis"
    echo "  - Windows: Download from https://redis.io/download"
fi
echo ""

# Task T013: Verify sentence-transformers model download
echo "Task T013: Downloading sentence-transformers model..."
python -c "
from sentence_transformers import SentenceTransformer
print('Downloading all-MiniLM-L6-v2 model...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('✓ Model downloaded and cached successfully')
" || echo "⚠ Failed to download model. Please check your internet connection."
echo ""

echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your API keys:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your GROQ_API_KEY and ANTHROPIC_API_KEY"
echo ""
echo "2. Verify environment:"
echo "   source .env"
echo "   python -c 'import utils.ai_router; print(\"Import successful\")'"
echo ""
echo "3. Run tests:"
echo "   pytest tests/ai_router/"
echo ""
echo "4. Start using the CLI:"
echo "   python utils/ai_router/cli.py --query \"What are the top job boards?\" --user_id test"
echo ""
