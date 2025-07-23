@echo off
REM GenXcover Web Frontend Startup Script for Windows
echo 🌐 Starting GenXcover Web Frontend...

REM Check if we're in the correct directory
if not exist "frontend-web" (
    echo ❌ Error: frontend-web directory not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Navigate to frontend-web directory
cd frontend-web

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed. Please install Node.js 16 or higher.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js detected
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ npm detected
npm --version

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Error: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

REM Check if backend is running
echo 🔍 Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Warning: Backend doesn't seem to be running at http://localhost:8000
    echo    Please start the backend first using one of:
    echo    - run_backend.bat
    echo    - python run_backend.py
    echo    - ./run_backend.sh ^(if using WSL/Git Bash^)
    echo.
    echo    The web frontend will still start, but API calls will fail.
) else (
    echo ✅ Backend is running at http://localhost:8000
)

REM Start the React development server
echo 🚀 Starting React development server...
echo 📍 Web app will be available at: http://localhost:3000
echo 🔗 Backend API proxy: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Set environment variables for development
set BROWSER=none
set GENERATE_SOURCEMAP=true

REM Start the development server
npm start

pause
