# GenXcover Backend Setup Guide

This guide provides multiple ways to run the GenXcover backend server.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Quick Start

The easiest way to run the backend is using one of the provided startup scripts:

### Option 1: Bash Script (macOS/Linux)
```bash
./run_backend.sh
```

### Option 2: Batch Script (Windows)
```cmd
run_backend.bat
```

### Option 3: Python Script (Cross-platform)
```bash
python3 run_backend.py
```
or
```bash
./run_backend.py
```

## What the Scripts Do

All scripts perform the following steps automatically:

1. **Environment Check**: Verify Python and pip are installed
2. **Virtual Environment**: Create a Python virtual environment in `backend/venv/`
3. **Dependencies**: Install all required packages from `requirements.txt`
4. **Configuration**: Check for `.env` file and create a basic one if missing
5. **Database**: Run migrations if Alembic is configured
6. **Server**: Start the FastAPI server with hot-reload enabled

## Manual Setup (Alternative)

If you prefer to set up manually:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - **macOS/Linux**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate.bat`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create/edit the `.env` file with your configuration:
   ```bash
   cp .env.example .env  # if available
   # or create manually with required variables
   ```

6. Run the server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Environment Configuration

The backend requires a `.env` file in the `backend/` directory. If it doesn't exist, the startup scripts will create a basic template:

```env
# Database Configuration
DATABASE_URL=sqlite:///./genxcover.db

# Development Settings
DEBUG=True
LOG_LEVEL=INFO

# OpenAI API Configuration (add your key)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Configuration (add your key)
TAVILY_API_KEY=your_tavily_api_key_here
```

### Required API Keys

To use all features, you'll need:

1. **OpenAI API Key**: For AI-powered music generation and lyrics
   - Get it from: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`

2. **Tavily API Key**: For enhanced search capabilities
   - Get it from: https://tavily.com/
   - Add to `.env`: `TAVILY_API_KEY=tvly-...`

## Server Information

Once running, the backend will be available at:

- **Main API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Key Features

The GenXcover backend provides:

- **User Authentication**: JWT-based auth system
- **Music Generation**: AI-powered song creation
- **Recording Studio**: Multi-track recording capabilities
- **Popularity Prediction**: AI-based hit prediction
- **Audio Processing**: Real-time audio analysis
- **RESTful API**: Full CRUD operations for songs, users, recordings

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

### Songs
- `GET /api/v1/songs/` - List songs
- `POST /api/v1/songs/` - Create song
- `GET /api/v1/songs/{id}` - Get song details
- `PUT /api/v1/songs/{id}` - Update song
- `DELETE /api/v1/songs/{id}` - Delete song

## Development

### Running Tests
```bash
cd backend
python -m pytest
```

### Code Formatting
```bash
cd backend
black .
isort .
```

### Database Migrations
If using Alembic for database migrations:
```bash
cd backend
alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   - Kill the process: `lsof -ti:8000 | xargs kill -9`
   - Or change the port in the startup scripts

2. **Python version issues**
   - Ensure Python 3.8+ is installed
   - Use `python3` instead of `python` if needed

3. **Permission denied (macOS/Linux)**
   - Make scripts executable: `chmod +x run_backend.sh run_backend.py`

4. **Virtual environment issues**
   - Delete `backend/venv/` and run the script again
   - Ensure you have sufficient disk space

5. **Dependency installation fails**
   - Update pip: `pip install --upgrade pip`
   - Check internet connection
   - Try installing dependencies individually

### Logs and Debugging

- Server logs are displayed in the terminal
- Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging
- Check `backend/logs/` directory if log files are configured

## Production Deployment

For production deployment, consider:

1. Use a production WSGI server like Gunicorn
2. Set up a reverse proxy (Nginx)
3. Use a production database (PostgreSQL)
4. Configure proper environment variables
5. Set up SSL/TLS certificates
6. Implement proper logging and monitoring

## Support

If you encounter issues:

1. Check the logs for error messages
2. Ensure all prerequisites are installed
3. Verify your `.env` configuration
4. Check the GitHub issues page
5. Contact the development team

---

**Happy coding! 🎵**
