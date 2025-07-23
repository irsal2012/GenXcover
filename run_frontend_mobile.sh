#!/bin/bash

# GenXcover Mobile Frontend Startup Script
echo "📱 Starting GenXcover Mobile Frontend..."

# Check if we're in the correct directory
if [ ! -d "frontend-mobile" ]; then
    echo "❌ Error: frontend-mobile directory not found. Please run this script from the project root."
    exit 1
fi

# Navigate to frontend-mobile directory
cd frontend-mobile

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

# Check if Expo CLI is installed globally
if ! command -v expo &> /dev/null; then
    echo "📦 Expo CLI not found. Installing globally..."
    npm install -g @expo/cli
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install Expo CLI."
        echo "   Try running: sudo npm install -g @expo/cli"
        exit 1
    fi
    echo "✅ Expo CLI installed successfully"
else
    echo "✅ Expo CLI $(expo --version) detected"
fi

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
    echo "   The mobile app will still start, but API calls will fail."
fi

# Display available options
echo ""
echo "🚀 Starting Expo development server..."
echo "📍 Choose how to run the mobile app:"
echo "   • Press 'i' to run on iOS simulator"
echo "   • Press 'a' to run on Android emulator"
echo "   • Press 'w' to run in web browser"
echo "   • Scan QR code with Expo Go app on your phone"
echo ""
echo "🔗 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Expo development server
expo start
