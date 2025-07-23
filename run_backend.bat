@echo off
REM GenXcover Backend Startup Script for Windows
echo 🎵 Starting GenXcover Backend Server...

REM Check if we're in the correct directory
if not exist "backend" (
    echo ❌ Error: backend directory not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Creating a basic one...
    (
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///./genxcover.db
        echo.
        echo # Development Settings
        echo DEBUG=True
        echo LOG_LEVEL=INFO
        echo.
        echo # OpenAI API Configuration ^(add your key^)
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Tavily API Configuration ^(add your key^)
        echo TAVILY_API_KEY=your_tavily_api_key_here
    ) > .env
    echo 📝 Please edit the .env file with your API keys before running the server.
)

REM Run database migrations (if alembic is set up)
if exist "alembic" (
    echo 🗄️  Running database migrations...
    alembic upgrade head
)

REM Start the FastAPI server
echo 🚀 Starting FastAPI server...
echo 📍 Server will be available at: http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo 🔍 Alternative docs: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the server using uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
