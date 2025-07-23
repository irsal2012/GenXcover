@echo off
REM GenXcover Mobile Frontend Startup Script for Windows
echo 📱 Starting GenXcover Mobile Frontend...

REM Check if we're in the correct directory
if not exist "frontend-mobile" (
    echo ❌ Error: frontend-mobile directory not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Navigate to frontend-mobile directory
cd frontend-mobile

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

REM Check if Expo CLI is installed globally
expo --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Expo CLI not found. Installing globally...
    npm install -g @expo/cli
    if errorlevel 1 (
        echo ❌ Error: Failed to install Expo CLI.
        echo    Try running as administrator or check your npm permissions.
        pause
        exit /b 1
    )
    echo ✅ Expo CLI installed successfully
) else (
    echo ✅ Expo CLI detected
    expo --version
)

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
    echo    The mobile app will still start, but API calls will fail.
) else (
    echo ✅ Backend is running at http://localhost:8000
)

REM Display available options
echo.
echo 🚀 Starting Expo development server...
echo 📍 Choose how to run the mobile app:
echo    • Press 'i' to run on iOS simulator
echo    • Press 'a' to run on Android emulator
echo    • Press 'w' to run in web browser
echo    • Scan QR code with Expo Go app on your phone
echo.
echo 🔗 Backend API: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Expo development server
expo start

pause
