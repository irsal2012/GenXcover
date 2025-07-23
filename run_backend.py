#!/usr/bin/env python3
"""
GenXcover Backend Startup Script
Cross-platform Python script to run the FastAPI backend server
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_status(message, emoji="ℹ️"):
    """Print a status message with emoji"""
    print(f"{emoji} {message}")

def check_python():
    """Check if Python is available and version is compatible"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_status("Error: Python 3.8 or higher is required", "❌")
            return False
        print_status(f"Python {version.major}.{version.minor}.{version.micro} detected", "✅")
        return True
    except Exception as e:
        print_status(f"Error checking Python version: {e}", "❌")
        return False

def check_directory():
    """Check if we're in the correct directory"""
    if not Path("backend").exists():
        print_status("Error: backend directory not found. Please run this script from the project root.", "❌")
        return False
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    backend_path = Path("backend")
    venv_path = backend_path / "venv"
    
    if not venv_path.exists():
        print_status("Creating virtual environment...", "📦")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print_status("Virtual environment created successfully", "✅")
        except subprocess.CalledProcessError as e:
            print_status(f"Error creating virtual environment: {e}", "❌")
            return False
    else:
        print_status("Virtual environment already exists", "✅")
    
    return True

def get_python_executable():
    """Get the path to the Python executable in the virtual environment"""
    backend_path = Path("backend")
    if platform.system() == "Windows":
        return backend_path / "venv" / "Scripts" / "python.exe"
    else:
        return backend_path / "venv" / "bin" / "python"

def get_pip_executable():
    """Get the path to the pip executable in the virtual environment"""
    backend_path = Path("backend")
    if platform.system() == "Windows":
        return backend_path / "venv" / "Scripts" / "pip.exe"
    else:
        return backend_path / "venv" / "bin" / "pip"

def install_dependencies():
    """Install Python dependencies"""
    print_status("Installing dependencies...", "📚")
    
    backend_path = Path("backend")
    requirements_path = backend_path / "requirements.txt"
    
    if not requirements_path.exists():
        print_status("Error: requirements.txt not found", "❌")
        return False
    
    pip_executable = get_pip_executable()
    
    try:
        # Upgrade pip first
        print_status("Upgrading pip...", "⬆️")
        subprocess.run([str(pip_executable), "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([str(pip_executable), "install", "-r", str(requirements_path)], check=True)
        print_status("Dependencies installed successfully", "✅")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Error installing dependencies: {e}", "❌")
        return False

def check_env_file():
    """Check if .env file exists and create a basic one if not"""
    backend_path = Path("backend")
    env_path = backend_path / ".env"
    
    if not env_path.exists():
        print_status("Warning: .env file not found. Creating a basic one...", "⚠️")
        
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///./genxcover.db

# Development Settings
DEBUG=True
LOG_LEVEL=INFO

# OpenAI API Configuration (add your key)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Configuration (add your key)
TAVILY_API_KEY=your_tavily_api_key_here
"""
        
        try:
            with open(env_path, 'w') as f:
                f.write(env_content)
            print_status("Basic .env file created. Please edit it with your API keys.", "📝")
        except Exception as e:
            print_status(f"Error creating .env file: {e}", "❌")
            return False
    
    return True

def run_server():
    """Start the FastAPI server"""
    print_status("Starting FastAPI server...", "🚀")
    print_status("Server will be available at: http://localhost:8000", "📍")
    print_status("API Documentation: http://localhost:8000/docs", "📖")
    print_status("Alternative docs: http://localhost:8000/redoc", "🔍")
    print()
    print_status("Press Ctrl+C to stop the server", "⏹️")
    print()
    
    python_executable = get_python_executable()
    backend_path = Path("backend")
    
    try:
        # Change to backend directory and run uvicorn
        os.chdir(backend_path)
        subprocess.run([
            str(python_executable), "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print_status("Server stopped by user", "⏹️")
    except subprocess.CalledProcessError as e:
        print_status(f"Error running server: {e}", "❌")
        return False
    
    return True

def main():
    """Main function"""
    print_status("Starting GenXcover Backend Server...", "🎵")
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_directory():
        sys.exit(1)
    
    # Setup environment
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main()
