#!/bin/bash
# Email Classification System Setup Script
# ProActive People - Recruitment Automation System

set -e  # Exit on error

echo "======================================================================"
echo "  Email Classification System - Setup"
echo "  ProActive People - Recruitment Automation"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠  Please edit .env and add your API keys${NC}"
    echo ""
fi

# Check Python dependencies
echo "Checking Python dependencies..."
if ! python -c "import groq" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install groq python-dotenv
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Python dependencies already installed${NC}"
fi
echo ""

# Check GROQ API key
echo "Checking GROQ API key..."
if grep -q "GROQ_API_KEY=your_" .env; then
    echo -e "${RED}✗ GROQ API key not configured${NC}"
    echo "Please update .env file with your GROQ API key"
    echo "Get your key from: https://console.groq.com/keys"
    exit 1
else
    echo -e "${GREEN}✓ GROQ API key configured${NC}"
fi
echo ""

# Test email classifier
echo "Testing email classifier..."
if python -c "from email_classifier import EmailClassifier; classifier = EmailClassifier()" 2>/dev/null; then
    echo -e "${GREEN}✓ Email classifier initialized successfully${NC}"
else
    echo -e "${RED}✗ Failed to initialize email classifier${NC}"
    exit 1
fi
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL client found${NC}"

    # Check if database exists
    if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw recruitment; then
        echo -e "${GREEN}✓ Database 'recruitment' exists${NC}"

        # Run migrations
        echo "Running email classification migrations..."
        if psql -U postgres -d recruitment -f data/migrations/007_create_email_tables.sql > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Migrations executed successfully${NC}"
        else
            echo -e "${YELLOW}⚠  Migrations may have already been run${NC}"
        fi
    else
        echo -e "${YELLOW}⚠  Database 'recruitment' not found${NC}"
        echo "Create database with: createdb -U postgres recruitment"
    fi
else
    echo -e "${YELLOW}⚠  PostgreSQL not found or not in PATH${NC}"
fi
echo ""

# Check Node.js for communication service
echo "Checking Node.js environment..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"

    # Check if node_modules exists in communication service
    if [ -d "backend/services/communication-service/node_modules" ]; then
        echo -e "${GREEN}✓ Communication service dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠  Communication service dependencies not installed${NC}"
        echo "Run: cd backend/services/communication-service && npm install"
    fi
else
    echo -e "${YELLOW}⚠  Node.js not found${NC}"
    echo "Install Node.js from: https://nodejs.org/"
fi
echo ""

# Run test suite
echo "======================================================================"
echo "  Running Test Suite"
echo "======================================================================"
echo ""

python test_email_classification.py

echo ""
echo "======================================================================"
echo "  Setup Complete!"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure Webhooks:"
echo "   - SendGrid: Point to https://your-domain/api/v1/emails/webhooks/sendgrid"
echo "   - AWS SES: Point to https://your-domain/api/v1/emails/webhooks/ses"
echo ""
echo "2. Start Services:"
echo "   cd backend/services/communication-service"
echo "   npm start"
echo ""
echo "3. Monitor Classifications:"
echo "   - API Docs: http://localhost:8089/api/docs"
echo "   - Statistics: GET /api/v1/emails/stats/overview"
echo "   - Review Queue: GET /api/v1/emails/review/needed"
echo ""
echo "4. Documentation:"
echo "   - README: EMAIL_CATEGORIZATION_README.md"
echo "   - Architecture: ARCHITECTURE.md"
echo ""
echo "======================================================================"
