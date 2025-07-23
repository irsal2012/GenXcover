# GenXcover - AI Music Generation & Analysis Platform

GenXcover is a comprehensive music generation and analysis platform that uses AI to create songs, lyrics, and provide popularity predictions. It features both web and mobile interfaces with advanced recording capabilities.

## Features

### 🎵 Music Generation
- **AI-powered lyrics generation** using OpenAI GPT-4
- **MIDI generation** for instrumental tracks
- **Audio synthesis** with voice cloning capabilities
- **Multi-format output** (audio, MIDI, lyrics)

### 🎙️ Advanced Recording Studio
- **Multi-track recording** with professional effects
- **Real-time audio processing** (reverb, delay, compression, EQ)
- **AI-assisted features** (harmony suggestions, vocal enhancement)
- **Auto-tune and pitch correction**

### 📊 Popularity Prediction
- **Audio feature analysis** (tempo, key, energy, spectral features)
- **Lyrics sentiment analysis** and theme detection
- **Market intelligence** integration
- **Commercial appeal scoring**

### 🌐 Multi-Platform Support
- **React web application** with Material-UI
- **React Native mobile app** (iOS/Android)
- **Real-time collaboration** features
- **Cloud storage** integration

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL/SQLite** - Database
- **Redis** - Caching and sessions
- **OpenAI GPT-4** - Lyrics generation
- **Librosa** - Audio analysis
- **PyTorch/TensorFlow** - ML models

### Frontend
- **React 18** with TypeScript
- **Material-UI** - Component library
- **Redux Toolkit** - State management
- **React Query** - API management
- **Web Audio API** - Audio processing

### Mobile
- **React Native** with TypeScript
- **Native audio modules** for recording
- **Redux Toolkit** - State management

## Project Structure

```
GenXcover/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   │   ├── music_generation/
│   │   │   ├── audio_processing/
│   │   │   ├── popularity_prediction/
│   │   │   └── recording/
│   │   └── schemas/        # Pydantic schemas
│   └── requirements.txt
├── frontend-web/           # React web app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── types/
│   └── package.json
├── frontend-mobile/        # React Native app
└── docker-compose.yml      # Development environment
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key

### Environment Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd GenXcover
```

2. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

3. **Using Docker (Recommended)**
```bash
docker-compose up --build
```

4. **Manual Setup**

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend-web
npm install
npm start
```

### API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/songs/generate` - Generate AI song
- `GET /api/v1/songs` - List public songs
- `POST /api/v1/songs` - Create custom song

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend-web
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend-web
npm test
```

## Features Implementation Status

### Phase 1: Foundation ✅
- [x] FastAPI backend setup
- [x] React web app setup
- [x] Authentication system
- [x] Database models
- [x] Basic API endpoints

### Phase 2: Core Music Generation 🚧
- [x] Lyrics generation with OpenAI
- [ ] MIDI generation system
- [ ] Audio synthesis
- [ ] Voice cloning integration

### Phase 3: Recording Studio 📋
- [ ] Multi-track recording
- [ ] Real-time effects
- [ ] AI-assisted features
- [ ] Export functionality

### Phase 4: Popularity Prediction 📋
- [ ] Audio analysis pipeline
- [ ] Lyrics analysis
- [ ] Market intelligence
- [ ] Prediction dashboard

### Phase 5: Mobile App 📋
- [ ] React Native setup
- [ ] Native audio modules
- [ ] Cross-platform features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@genxcover.com or join our Discord community.
