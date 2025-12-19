#!/bin/bash

# DS-STAR Setup Script
# This script sets up both the backend and frontend for the DS-STAR agent

set -e  # Exit on error

echo "======================================"
echo "DS-STAR Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js version 18 or higher is required${NC}"
    echo "Current version: $(node -v)"
    exit 1
fi

echo -e "${GREEN}✓${NC} Prerequisites check passed"
echo ""

# Setup Backend
echo "======================================"
echo "Setting up Backend Server"
echo "======================================"
cd backend

echo "Installing Python dependencies..."
pip install -e ".[ml]"

echo ""
echo -e "${GREEN}✓${NC} Backend setup complete"
echo ""

# Setup Frontend
cd ../frontend
echo "======================================"
echo "Setting up Frontend Application"
echo "======================================"

echo "Installing Node.js dependencies..."
npm install

echo ""
echo -e "${GREEN}✓${NC} Frontend setup complete"
echo ""

# Check for OpenAI API key
cd ..
echo "======================================"
echo "Environment Configuration"
echo "======================================"

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable is not set${NC}"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY=\"sk-your-key-here\""
    echo ""
else
    echo -e "${GREEN}✓${NC} OPENAI_API_KEY is set"
    echo ""
fi

# Ensure start script is executable
if [ -f "start.sh" ]; then
    chmod +x start.sh
    echo -e "${GREEN}✓${NC} Start script is ready"
else
    echo -e "${YELLOW}Note: start.sh not found. You may need to create it.${NC}"
fi
echo ""

# Print instructions
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the application, simply run:"
echo ""
echo -e "   ${GREEN}./start.sh${NC}"
echo ""
echo "This will start both the backend and frontend together."
echo ""
echo "The application will be available at:"
echo -e "   ${GREEN}http://localhost:3000${NC}"
echo ""
echo "Press Ctrl+C to stop both services."
echo ""
echo "For manual setup instructions, see:"
echo "  - README_FRONTEND.md (main setup guide)"
echo "  - frontend/README.md (frontend documentation)"
echo ""
echo -e "${GREEN}Happy analyzing! 🚀${NC}"
echo ""
