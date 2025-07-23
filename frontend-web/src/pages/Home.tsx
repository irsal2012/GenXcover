import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { songsAPI } from '../services/api';
import { GENRES, VOICE_TYPES, STYLES, SongGenerate } from '../types';
import './Home.css';

interface GenerationResult {
  type: 'full' | 'lyrics' | 'instrumental' | 'remix';
  data: any;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  const [activeTab, setActiveTab] = useState<'full' | 'lyrics' | 'instrumental' | 'remix'>('full');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResult | null>(null);

  // Full song generation form state
  const [fullSongForm, setFullSongForm] = useState<SongGenerate>({
    title: '',
    genre: 'Pop',
    style: 'Upbeat',
    theme: '',
    voice_type: 'Male',
    custom_prompt: '',
    include_audio: true,
    include_midi: true,
  });

  // Lyrics only form state
  const [lyricsForm, setLyricsForm] = useState({
    title: '',
    genre: 'Pop',
    theme: '',
    style: 'Upbeat',
    custom_prompt: '',
  });

  // Instrumental form state
  const [instrumentalForm, setInstrumentalForm] = useState({
    title: '',
    genre: 'Pop',
    key: 'C',
    tempo: 120,
    duration: 180,
    style: 'Upbeat',
    include_audio: true,
  });

  // Remix form state
  const [remixForm, setRemixForm] = useState({
    song_id: '',
    new_genre: 'Pop',
    new_tempo: 120,
    new_key: 'C',
  });

  const [userSongs, setUserSongs] = useState<any[]>([]);

  useEffect(() => {
    if (isAuthenticated) {
      loadUserSongs();
    }
  }, [isAuthenticated]);

  const loadUserSongs = async () => {
    try {
      const songs = await songsAPI.getMySongs();
      setUserSongs(songs);
    } catch (error) {
      console.error('Failed to load user songs:', error);
    }
  };

  const handleFullSongGeneration = async () => {
    if (!fullSongForm.title.trim()) {
      setError('Please enter a song title');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await songsAPI.generateSong(fullSongForm);
      setResult({ type: 'full', data: result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to generate song');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLyricsGeneration = async () => {
    if (!lyricsForm.title.trim()) {
      setError('Please enter a song title');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await songsAPI.generateLyricsOnly(lyricsForm);
      setResult({ type: 'lyrics', data: result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to generate lyrics');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstrumentalGeneration = async () => {
    if (!instrumentalForm.title.trim()) {
      setError('Please enter a song title');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await songsAPI.generateInstrumental(instrumentalForm);
      setResult({ type: 'instrumental', data: result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to generate instrumental');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemixGeneration = async () => {
    if (!remixForm.song_id) {
      setError('Please select a song to remix');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await songsAPI.remixSong(parseInt(remixForm.song_id), {
        new_genre: remixForm.new_genre,
        new_tempo: remixForm.new_tempo,
        new_key: remixForm.new_key,
      });
      setResult({ type: 'remix', data: result });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to remix song');
    } finally {
      setIsLoading(false);
    }
  };

  const renderFullSongForm = () => (
    <div className="form-container">
      <form className="generation-form" onSubmit={(e) => { e.preventDefault(); handleFullSongGeneration(); }}>
        <div className="form-section">
          <h3>🎵 Song Details</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Song Title *</label>
              <input
                type="text"
                value={fullSongForm.title}
                onChange={(e) => setFullSongForm({ ...fullSongForm, title: e.target.value })}
                placeholder="Enter your song title..."
                required
              />
            </div>
            <div className="form-group">
              <label>Genre</label>
              <select
                value={fullSongForm.genre}
                onChange={(e) => setFullSongForm({ ...fullSongForm, genre: e.target.value })}
              >
                {GENRES.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Style</label>
              <select
                value={fullSongForm.style}
                onChange={(e) => setFullSongForm({ ...fullSongForm, style: e.target.value })}
              >
                {STYLES.map(style => (
                  <option key={style} value={style}>{style}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Voice Type</label>
              <select
                value={fullSongForm.voice_type}
                onChange={(e) => setFullSongForm({ ...fullSongForm, voice_type: e.target.value })}
              >
                {VOICE_TYPES.map(voice => (
                  <option key={voice} value={voice}>{voice}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Theme (Optional)</label>
            <input
              type="text"
              value={fullSongForm.theme}
              onChange={(e) => setFullSongForm({ ...fullSongForm, theme: e.target.value })}
              placeholder="e.g., love, adventure, nostalgia..."
            />
          </div>
          <div className="form-group">
            <label>Custom Prompt (Optional)</label>
            <textarea
              value={fullSongForm.custom_prompt}
              onChange={(e) => setFullSongForm({ ...fullSongForm, custom_prompt: e.target.value })}
              placeholder="Describe any specific requirements or ideas for your song..."
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h3>🎼 Output Options</h3>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={fullSongForm.include_audio}
                onChange={(e) => setFullSongForm({ ...fullSongForm, include_audio: e.target.checked })}
              />
              <span>Generate Audio File</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={fullSongForm.include_midi}
                onChange={(e) => setFullSongForm({ ...fullSongForm, include_midi: e.target.checked })}
              />
              <span>Generate MIDI File</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          className="generate-btn primary"
          disabled={isLoading}
        >
          {isLoading ? '🎵 Generating...' : '🎵 Generate Full Song'}
        </button>
      </form>
    </div>
  );

  const renderLyricsForm = () => (
    <div className="form-container">
      <form className="generation-form" onSubmit={(e) => { e.preventDefault(); handleLyricsGeneration(); }}>
        <div className="form-section">
          <h3>📝 Lyrics Generation</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Song Title *</label>
              <input
                type="text"
                value={lyricsForm.title}
                onChange={(e) => setLyricsForm({ ...lyricsForm, title: e.target.value })}
                placeholder="Enter your song title..."
                required
              />
            </div>
            <div className="form-group">
              <label>Genre</label>
              <select
                value={lyricsForm.genre}
                onChange={(e) => setLyricsForm({ ...lyricsForm, genre: e.target.value })}
              >
                {GENRES.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Style</label>
              <select
                value={lyricsForm.style}
                onChange={(e) => setLyricsForm({ ...lyricsForm, style: e.target.value })}
              >
                {STYLES.map(style => (
                  <option key={style} value={style}>{style}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Theme (Optional)</label>
              <input
                type="text"
                value={lyricsForm.theme}
                onChange={(e) => setLyricsForm({ ...lyricsForm, theme: e.target.value })}
                placeholder="e.g., love, adventure, nostalgia..."
              />
            </div>
          </div>
          <div className="form-group">
            <label>Custom Prompt (Optional)</label>
            <textarea
              value={lyricsForm.custom_prompt}
              onChange={(e) => setLyricsForm({ ...lyricsForm, custom_prompt: e.target.value })}
              placeholder="Describe the story, mood, or specific elements you want in the lyrics..."
              rows={3}
            />
          </div>
        </div>

        <button
          type="submit"
          className="generate-btn secondary"
          disabled={isLoading}
        >
          {isLoading ? '📝 Generating...' : '📝 Generate Lyrics'}
        </button>
      </form>
    </div>
  );

  const renderInstrumentalForm = () => (
    <div className="form-container">
      <form className="generation-form" onSubmit={(e) => { e.preventDefault(); handleInstrumentalGeneration(); }}>
        <div className="form-section">
          <h3>🎼 Instrumental Generation</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Track Title *</label>
              <input
                type="text"
                value={instrumentalForm.title}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, title: e.target.value })}
                placeholder="Enter track title..."
                required
              />
            </div>
            <div className="form-group">
              <label>Genre</label>
              <select
                value={instrumentalForm.genre}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, genre: e.target.value })}
              >
                {GENRES.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Key</label>
              <select
                value={instrumentalForm.key}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, key: e.target.value })}
              >
                {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                  <option key={key} value={key}>{key}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Tempo (BPM)</label>
              <input
                type="number"
                value={instrumentalForm.tempo}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, tempo: parseInt(e.target.value) })}
                min="60"
                max="200"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Duration (seconds)</label>
              <input
                type="number"
                value={instrumentalForm.duration}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, duration: parseInt(e.target.value) })}
                min="30"
                max="600"
              />
            </div>
            <div className="form-group">
              <label>Style</label>
              <select
                value={instrumentalForm.style}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, style: e.target.value })}
              >
                {STYLES.map(style => (
                  <option key={style} value={style}>{style}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={instrumentalForm.include_audio}
                onChange={(e) => setInstrumentalForm({ ...instrumentalForm, include_audio: e.target.checked })}
              />
              <span>Generate Audio File</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          className="generate-btn tertiary"
          disabled={isLoading}
        >
          {isLoading ? '🎼 Generating...' : '🎼 Generate Instrumental'}
        </button>
      </form>
    </div>
  );

  const renderRemixForm = () => (
    <div className="form-container">
      <form className="generation-form" onSubmit={(e) => { e.preventDefault(); handleRemixGeneration(); }}>
        <div className="form-section">
          <h3>🔄 Remix Existing Song</h3>
          <div className="form-group">
            <label>Select Song to Remix *</label>
            <select
              value={remixForm.song_id}
              onChange={(e) => setRemixForm({ ...remixForm, song_id: e.target.value })}
              required
            >
              <option value="">Choose a song...</option>
              {userSongs.map(song => (
                <option key={song.id} value={song.id}>{song.title} ({song.genre})</option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>New Genre</label>
              <select
                value={remixForm.new_genre}
                onChange={(e) => setRemixForm({ ...remixForm, new_genre: e.target.value })}
              >
                {GENRES.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>New Tempo (BPM)</label>
              <input
                type="number"
                value={remixForm.new_tempo}
                onChange={(e) => setRemixForm({ ...remixForm, new_tempo: parseInt(e.target.value) })}
                min="60"
                max="200"
              />
            </div>
          </div>
          <div className="form-group">
            <label>New Key</label>
            <select
              value={remixForm.new_key}
              onChange={(e) => setRemixForm({ ...remixForm, new_key: e.target.value })}
            >
              {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                <option key={key} value={key}>{key}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="generate-btn"
          disabled={isLoading || !remixForm.song_id}
        >
          {isLoading ? '🔄 Remixing...' : '🔄 Create Remix'}
        </button>
      </form>
    </div>
  );

  const renderResults = () => {
    if (!result) return null;

    return (
      <div className="results-container">
        {result.type === 'lyrics' && (
          <div className="result-section">
            <h2 className="result-title">📝 Generated Lyrics</h2>
            <div className="lyrics-content">
              <pre>{result.data.lyrics}</pre>
            </div>
          </div>
        )}

        {result.type === 'instrumental' && (
          <div className="result-section">
            <h2 className="result-title">🎼 Generated Instrumental</h2>
            <p>Title: {result.data.title}</p>
            <p>Genre: {result.data.genre} | Key: {result.data.key} | Tempo: {result.data.tempo} BPM</p>
            {result.data.audio_file_path && (
              <div className="audio-player">
                <audio controls>
                  <source src={result.data.audio_file_path} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        )}

        {result.type === 'full' && (
          <div className="result-section">
            <h2 className="result-title">🎵 Generated Song</h2>
            <p>Title: {result.data.title}</p>
            <p>Genre: {result.data.genre} | Style: {result.data.style}</p>
            {result.data.lyrics && (
              <div className="lyrics-content">
                <pre>{result.data.lyrics}</pre>
              </div>
            )}
            {result.data.audio_file_path && (
              <div className="audio-player">
                <audio controls>
                  <source src={result.data.audio_file_path} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        )}

        {result.type === 'remix' && (
          <div className="result-section">
            <h2 className="result-title">🔄 Remixed Song</h2>
            <p>Title: {result.data.title}</p>
            <p>Original: {result.data.original_genre} → New: {result.data.new_genre}</p>
            {result.data.audio_file_path && (
              <div className="audio-player">
                <audio controls>
                  <source src={result.data.audio_file_path} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (!isAuthenticated) {
    return (
      <div className="home-container">
        <div className="header-section">
          <h1 className="page-title">Welcome to GenXcover</h1>
          <p className="page-subtitle">
            Create amazing music with AI-powered generation tools. Please log in to get started.
          </p>
          <div style={{ marginTop: '2rem' }}>
            <button 
              className="generate-btn primary" 
              onClick={() => navigate('/login')}
              style={{ marginRight: '1rem' }}
            >
              Login
            </button>
            <button 
              className="generate-btn secondary" 
              onClick={() => navigate('/register')}
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="header-section">
        <h1 className="page-title">AI Music Generation</h1>
        <p className="page-subtitle">
          Create original music, lyrics, and instrumentals with the power of artificial intelligence.
          Choose your generation type and let creativity flow.
        </p>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'full' ? 'active' : ''}`}
            onClick={() => setActiveTab('full')}
          >
            🎵 Full Song
          </button>
          <button
            className={`tab ${activeTab === 'lyrics' ? 'active' : ''}`}
            onClick={() => setActiveTab('lyrics')}
          >
            📝 Lyrics Only
          </button>
          <button
            className={`tab ${activeTab === 'instrumental' ? 'active' : ''}`}
            onClick={() => setActiveTab('instrumental')}
          >
            🎼 Instrumental
          </button>
          <button
            className={`tab ${activeTab === 'remix' ? 'active' : ''}`}
            onClick={() => setActiveTab('remix')}
          >
            🔄 Remix
          </button>
        </div>
      </div>

      <div className="content-container">
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {activeTab === 'full' && renderFullSongForm()}
        {activeTab === 'lyrics' && renderLyricsForm()}
        {activeTab === 'instrumental' && renderInstrumentalForm()}
        {activeTab === 'remix' && renderRemixForm()}

        {renderResults()}
      </div>
    </div>
  );
};

export default Home;
