#!/bin/bash

# GenXcover Web Frontend Startup Script
echo "🌐 Starting GenXcover Web Frontend..."

# Check if we're in the correct directory
if [ ! -d "frontend-web" ]; then
    echo "❌ Error: frontend-web directory not found. Please run this script from the project root."
    exit 1
fi

# Navigate to frontend-web directory
cd frontend-web

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed. Please install Node.js 16 or higher."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Error: Node.js version 16 or higher is required. Current version: $(node --version)"
    echo "   Please update Node.js from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm $(npm --version) detected"

# Install dependencies if node_modules doesn't exist or package.json is newer
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies."
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Warning: Backend doesn't seem to be running at http://localhost:8000"
    echo "   Please start the backend first using one of:"
    echo "   - ./run_backend.sh"
    echo "   - python3 run_backend.py"
    echo "   - run_backend.bat (Windows)"
    echo ""
    echo "   The web frontend will still start, but API calls will fail."
fi

# Start the React development server
echo "🚀 Starting React development server..."
echo "📍 Web app will be available at: http://localhost:3000"
echo "🔗 Backend API proxy: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set environment variables for development
export BROWSER=none  # Prevent auto-opening browser
export GENERATE_SOURCEMAP=true

# Start the development server
npm start
