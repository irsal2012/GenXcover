#!/bin/bash

# GenXcover Backend Startup Script
echo "🎵 Starting GenXcover Backend Server..."

# Check if we're in the correct directory
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found. Please run this script from the project root."
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating a basic one..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./genxcover.db

# Development Settings
DEBUG=True
LOG_LEVEL=INFO

# OpenAI API Configuration (add your key)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Configuration (add your key)
TAVILY_API_KEY=your_tavily_api_key_here
EOF
    echo "📝 Please edit the .env file with your API keys before running the server."
fi

# Run database migrations (if alembic is set up)
if [ -d "alembic" ]; then
    echo "🗄️  Running database migrations..."
    alembic upgrade head
fi

# Start the FastAPI server
echo "🚀 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Alternative docs: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server using uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
