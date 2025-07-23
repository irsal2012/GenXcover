# GenXcover Frontend Setup Guide

This guide provides instructions for running both the web and mobile frontends of the GenXcover application.

## Prerequisites

- Node.js 16 or higher
- npm (comes with Node.js)
- For mobile development: Expo CLI
- For mobile testing: Expo Go app on your phone (optional)

## Quick Start

### Web Frontend

Choose one of these methods to run the web frontend:

#### Option 1: Bash Script (macOS/Linux)
```bash
./run_frontend_web.sh
```

#### Option 2: Batch Script (Windows)
```cmd
run_frontend_web.bat
```

#### Option 3: Manual Setup
```bash
cd frontend-web
npm install
npm start
```

### Mobile Frontend

Choose one of these methods to run the mobile frontend:

#### Option 1: Bash Script (macOS/Linux)
```bash
./run_frontend_mobile.sh
```

#### Option 2: Batch Script (Windows)
```cmd
run_frontend_mobile.bat
```

#### Option 3: Manual Setup
```bash
cd frontend-mobile
npm install -g @expo/cli  # if not already installed
npm install
expo start
```

## What the Scripts Do

### Web Frontend Scripts
1. **Environment Check**: Verify Node.js and npm are installed
2. **Dependencies**: Install React and related packages
3. **Backend Check**: Verify backend is running on port 8000
4. **Development Server**: Start React dev server on port 3000

### Mobile Frontend Scripts
1. **Environment Check**: Verify Node.js and npm are installed
2. **Expo CLI**: Install Expo CLI globally if not present
3. **Dependencies**: Install React Native and Expo packages
4. **Backend Check**: Verify backend is running on port 8000
5. **Development Server**: Start Expo dev server with QR code

## Server Information

### Web Frontend
- **Development Server**: http://localhost:3000
- **Backend Proxy**: Automatically proxies API calls to http://localhost:8000
- **Hot Reload**: Enabled for development

### Mobile Frontend
- **Expo DevTools**: Opens in browser automatically
- **iOS Simulator**: Press 'i' in terminal
- **Android Emulator**: Press 'a' in terminal
- **Web Browser**: Press 'w' in terminal
- **Physical Device**: Scan QR code with Expo Go app

## Technology Stack

### Web Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Audio**: Tone.js, WaveSurfer.js
- **Forms**: React Hook Form with Yup validation

### Mobile Frontend
- **Framework**: React Native with Expo
- **Language**: TypeScript
- **UI Library**: React Native Paper
- **Navigation**: React Navigation
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios
- **Audio**: Expo AV
- **File System**: Expo File System

## Development Features

### Web Frontend Features
- **Recording Studio**: Multi-track audio recording
- **Music Generation**: AI-powered song creation
- **Popularity Prediction**: Hit prediction analysis
- **User Authentication**: JWT-based auth
- **Responsive Design**: Works on desktop and mobile browsers

### Mobile Frontend Features
- **Native Recording**: Device microphone access
- **Touch Interface**: Optimized for mobile interaction
- **Offline Support**: Local storage capabilities
- **Push Notifications**: Real-time updates
- **Camera Integration**: Profile pictures and media

## API Integration

Both frontends connect to the backend API at `http://localhost:8000`:

### Key Endpoints
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/songs/` - List user songs
- `POST /api/v1/songs/` - Create new song
- `POST /api/v1/songs/generate` - AI song generation
- `POST /api/v1/recordings/` - Upload recordings
- `GET /api/v1/predictions/{id}` - Get popularity prediction

## Environment Configuration

### Web Frontend (.env)
Create `frontend-web/.env` for custom configuration:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true
```

### Mobile Frontend (.env)
Create `frontend-mobile/.env` for custom configuration:
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_ENVIRONMENT=development
```

## Troubleshooting

### Common Issues

#### Web Frontend

1. **Port 3000 already in use**
   ```bash
   lsof -ti:3000 | xargs kill -9
   # Or set custom port: PORT=3001 npm start
   ```

2. **Node modules issues**
   ```bash
   cd frontend-web
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Proxy errors**
   - Ensure backend is running on port 8000
   - Check `proxy` setting in `package.json`

#### Mobile Frontend

1. **Expo CLI not found**
   ```bash
   npm install -g @expo/cli
   # Or use npx: npx expo start
   ```

2. **Metro bundler issues**
   ```bash
   cd frontend-mobile
   npx expo start --clear
   ```

3. **Device connection issues**
   - Ensure phone and computer are on same network
   - Try using tunnel mode: `npx expo start --tunnel`

4. **iOS Simulator not opening**
   - Install Xcode and iOS Simulator
   - Run: `sudo xcode-select --install`

5. **Android Emulator not opening**
   - Install Android Studio
   - Create and start an AVD (Android Virtual Device)

### Performance Issues

1. **Slow build times**
   - Clear npm cache: `npm cache clean --force`
   - Update Node.js to latest LTS version

2. **Memory issues**
   - Increase Node.js memory: `export NODE_OPTIONS="--max-old-space-size=4096"`

## Development Workflow

### Recommended Development Setup

1. **Start Backend** (in terminal 1):
   ```bash
   ./run_backend.sh
   ```

2. **Start Web Frontend** (in terminal 2):
   ```bash
   ./run_frontend_web.sh
   ```

3. **Start Mobile Frontend** (in terminal 3):
   ```bash
   ./run_frontend_mobile.sh
   ```

### Code Structure

#### Web Frontend Structure
```
frontend-web/
├── public/          # Static assets
├── src/
│   ├── components/  # Reusable components
│   ├── pages/       # Page components
│   ├── services/    # API services
│   ├── store/       # Redux store
│   ├── types/       # TypeScript types
│   └── App.tsx      # Main app component
└── package.json
```

#### Mobile Frontend Structure
```
frontend-mobile/
├── src/
│   ├── components/  # Reusable components
│   ├── screens/     # Screen components
│   ├── services/    # API services
│   ├── hooks/       # Custom hooks
│   └── navigation/  # Navigation setup
├── app.json         # Expo configuration
└── package.json
```

## Building for Production

### Web Frontend
```bash
cd frontend-web
npm run build
# Builds to frontend-web/build/
```

### Mobile Frontend
```bash
cd frontend-mobile
npx expo build:web      # Web build
npx eas build --platform ios    # iOS build (requires EAS)
npx eas build --platform android # Android build (requires EAS)
```

## Testing

### Web Frontend
```bash
cd frontend-web
npm test              # Run tests
npm run test:coverage # Run with coverage
```

### Mobile Frontend
```bash
cd frontend-mobile
npm test              # Run tests
npx expo test         # Expo-specific tests
```

## Support

If you encounter issues:

1. Check that Node.js version is 16 or higher
2. Ensure backend is running on port 8000
3. Clear node_modules and reinstall dependencies
4. Check the browser console for errors
5. Review the terminal output for error messages

For mobile-specific issues:
1. Check Expo CLI version: `expo --version`
2. Verify device/emulator connectivity
3. Try clearing Metro cache: `npx expo start --clear`
4. Check Expo documentation: https://docs.expo.dev/

---

**Happy coding! 🎵📱**
