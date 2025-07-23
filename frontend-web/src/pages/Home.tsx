import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store';
import { songsAPI } from '../services/api';
import { Song, Genre, VoiceType, Style, GENRES, VOICE_TYPES, STYLES } from '../types';
import './Home.css';

interface GenerationForm {
  title: string;
  genre: Genre;
  style: Style;
  theme: string;
  voice_type: VoiceType;
  custom_prompt: string;
  include_audio: boolean;
  include_midi: boolean;
  key: string;
  tempo: number;
  duration: number;
}

interface GenerationSuggestions {
  genre: string;
  recommended_tempos: number[];
  recommended_keys: string[];
  recommended_styles: string[];
  recommended_voice_types: string[];
  theme_suggestions: string[];
}

const Home: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { songs, isLoading } = useSelector((state: RootState) => state.songs);

  const [activeTab, setActiveTab] = useState<'generate' | 'lyrics' | 'instrumental'>('generate');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState('');
  const [generatedSong, setGeneratedSong] = useState<Song | null>(null);
  const [suggestions, setSuggestions] = useState<GenerationSuggestions | null>(null);
  const [recentSongs, setRecentSongs] = useState<Song[]>([]);

  const [form, setForm] = useState<GenerationForm>({
    title: '',
    genre: 'Pop',
    style: 'Upbeat',
    theme: '',
    voice_type: 'Male',
    custom_prompt: '',
    include_audio: true,
    include_midi: true,
    key: 'C',
    tempo: 120,
    duration: 180
  });

  const [lyricsForm, setLyricsForm] = useState({
    title: '',
    genre: 'Pop' as Genre,
    theme: '',
    style: 'Upbeat' as Style,
    custom_prompt: ''
  });

  const [instrumentalForm, setInstrumentalForm] = useState({
    title: '',
    genre: 'Pop' as Genre,
    key: 'C',
    tempo: 120,
    duration: 180,
    style: 'Upbeat' as Style,
    include_audio: true
  });

  const [generatedLyrics, setGeneratedLyrics] = useState<any>(null);
  const [generatedInstrumental, setGeneratedInstrumental] = useState<any>(null);

  const keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

  useEffect(() => {
    loadRecentSongs();
  }, []);

  useEffect(() => {
    if (form.genre) {
      loadSuggestions(form.genre, form.theme);
    }
  }, [form.genre, form.theme]);

  const loadRecentSongs = async () => {
    try {
      const response = await songsAPI.getSongs({ limit: 6 });
      setRecentSongs(response.songs);
    } catch (error) {
      console.error('Failed to load recent songs:', error);
    }
  };

  const loadSuggestions = async (genre: string, theme?: string) => {
    try {
      const suggestions = await songsAPI.getGenerationSuggestions(genre, theme);
      setSuggestions(suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleFormChange = (field: keyof GenerationForm, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleLyricsFormChange = (field: string, value: any) => {
    setLyricsForm(prev => ({ ...prev, [field]: value }));
  };

  const handleInstrumentalFormChange = (field: string, value: any) => {
    setInstrumentalForm(prev => ({ ...prev, [field]: value }));
  };

  const generateCompleteSong = async () => {
    if (!form.title.trim()) {
      alert('Please enter a song title');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress('Initializing song generation...');
    setGeneratedSong(null);

    try {
      setGenerationProgress('Generating lyrics...');
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate progress

      setGenerationProgress('Creating musical arrangement...');
      await new Promise(resolve => setTimeout(resolve, 1500));

      setGenerationProgress('Synthesizing audio...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      const song = await songsAPI.generateSong({
        title: form.title,
        genre: form.genre,
        style: form.style,
        theme: form.theme || undefined,
        voice_type: form.voice_type,
        custom_prompt: form.custom_prompt || undefined,
        include_audio: form.include_audio,
        include_midi: form.include_midi
      });

      setGeneratedSong(song);
      setGenerationProgress('Song generation complete!');
      loadRecentSongs(); // Refresh recent songs
    } catch (error: any) {
      console.error('Failed to generate song:', error);
      setGenerationProgress(`Error: ${error.response?.data?.detail || 'Failed to generate song'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateLyricsOnly = async () => {
    if (!lyricsForm.title.trim()) {
      alert('Please enter a song title');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress('Generating lyrics...');
    setGeneratedLyrics(null);

    try {
      const result = await songsAPI.generateLyricsOnly(lyricsForm);
      setGeneratedLyrics(result);
      setGenerationProgress('Lyrics generation complete!');
    } catch (error: any) {
      console.error('Failed to generate lyrics:', error);
      setGenerationProgress(`Error: ${error.response?.data?.detail || 'Failed to generate lyrics'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateInstrumentalOnly = async () => {
    if (!instrumentalForm.title.trim()) {
      alert('Please enter a track title');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress('Generating instrumental track...');
    setGeneratedInstrumental(null);

    try {
      const result = await songsAPI.generateInstrumental(instrumentalForm);
      setGeneratedInstrumental(result);
      setGenerationProgress('Instrumental generation complete!');
    } catch (error: any) {
      console.error('Failed to generate instrumental:', error);
      setGenerationProgress(`Error: ${error.response?.data?.detail || 'Failed to generate instrumental'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const applySuggestion = (field: string, value: any) => {
    if (activeTab === 'generate') {
      handleFormChange(field as keyof GenerationForm, value);
    } else if (activeTab === 'lyrics') {
      handleLyricsFormChange(field, value);
    } else if (activeTab === 'instrumental') {
      handleInstrumentalFormChange(field, value);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-icon">🎵</div>
          <h1>Music Generation</h1>
          <p>Create AI-powered music with advanced algorithms and machine learning.</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Generation Tabs */}
        <div className="generation-tabs">
          <button
            className={`tab-button ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
          >
            Complete Song
          </button>
          <button
            className={`tab-button ${activeTab === 'lyrics' ? 'active' : ''}`}
            onClick={() => setActiveTab('lyrics')}
          >
            Lyrics Only
          </button>
          <button
            className={`tab-button ${activeTab === 'instrumental' ? 'active' : ''}`}
            onClick={() => setActiveTab('instrumental')}
          >
            Instrumental
          </button>
        </div>

        <div className="content-grid">
          {/* Generation Form */}
          <div className="generation-panel">
            {activeTab === 'generate' && (
              <div className="form-section">
                <h3>Generate Complete Song</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Song Title *</label>
                    <input
                      type="text"
                      value={form.title}
                      onChange={(e) => handleFormChange('title', e.target.value)}
                      placeholder="Enter song title..."
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Genre</label>
                    <select
                      value={form.genre}
                      onChange={(e) => handleFormChange('genre', e.target.value as Genre)}
                      className="form-select"
                    >
                      {GENRES.map(genre => (
                        <option key={genre} value={genre}>{genre}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Style</label>
                    <select
                      value={form.style}
                      onChange={(e) => handleFormChange('style', e.target.value as Style)}
                      className="form-select"
                    >
                      {STYLES.map(style => (
                        <option key={style} value={style}>{style}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Voice Type</label>
                    <select
                      value={form.voice_type}
                      onChange={(e) => handleFormChange('voice_type', e.target.value as VoiceType)}
                      className="form-select"
                    >
                      {VOICE_TYPES.map(voice => (
                        <option key={voice} value={voice}>{voice}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Theme</label>
                    <input
                      type="text"
                      value={form.theme}
                      onChange={(e) => handleFormChange('theme', e.target.value)}
                      placeholder="e.g., Love, Freedom, Adventure..."
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Key</label>
                    <select
                      value={form.key}
                      onChange={(e) => handleFormChange('key', e.target.value)}
                      className="form-select"
                    >
                      {keys.map(key => (
                        <option key={key} value={key}>{key}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Tempo (BPM)</label>
                    <input
                      type="number"
                      value={form.tempo}
                      onChange={(e) => handleFormChange('tempo', parseInt(e.target.value))}
                      min="60"
                      max="200"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Duration (seconds)</label>
                    <input
                      type="number"
                      value={form.duration}
                      onChange={(e) => handleFormChange('duration', parseInt(e.target.value))}
                      min="30"
                      max="600"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group full-width">
                    <label>Custom Prompt (Optional)</label>
                    <textarea
                      value={form.custom_prompt}
                      onChange={(e) => handleFormChange('custom_prompt', e.target.value)}
                      placeholder="Additional instructions for the AI..."
                      className="form-textarea"
                      rows={3}
                    />
                  </div>

                  <div className="form-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={form.include_audio}
                        onChange={(e) => handleFormChange('include_audio', e.target.checked)}
                      />
                      Generate Audio
                    </label>
                  </div>

                  <div className="form-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={form.include_midi}
                        onChange={(e) => handleFormChange('include_midi', e.target.checked)}
                      />
                      Generate MIDI
                    </label>
                  </div>
                </div>

                <button
                  onClick={generateCompleteSong}
                  disabled={isGenerating || !form.title.trim()}
                  className="generate-button"
                >
                  {isGenerating ? 'Generating...' : 'Generate Music'}
                </button>
              </div>
            )}

            {activeTab === 'lyrics' && (
              <div className="form-section">
                <h3>Generate Lyrics Only</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Song Title *</label>
                    <input
                      type="text"
                      value={lyricsForm.title}
                      onChange={(e) => handleLyricsFormChange('title', e.target.value)}
                      placeholder="Enter song title..."
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Genre</label>
                    <select
                      value={lyricsForm.genre}
                      onChange={(e) => handleLyricsFormChange('genre', e.target.value)}
                      className="form-select"
                    >
                      {GENRES.map(genre => (
                        <option key={genre} value={genre}>{genre}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Style</label>
                    <select
                      value={lyricsForm.style}
                      onChange={(e) => handleLyricsFormChange('style', e.target.value)}
                      className="form-select"
                    >
                      {STYLES.map(style => (
                        <option key={style} value={style}>{style}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Theme</label>
                    <input
                      type="text"
                      value={lyricsForm.theme}
                      onChange={(e) => handleLyricsFormChange('theme', e.target.value)}
                      placeholder="e.g., Love, Freedom, Adventure..."
                      className="form-input"
                    />
                  </div>

                  <div className="form-group full-width">
                    <label>Custom Prompt (Optional)</label>
                    <textarea
                      value={lyricsForm.custom_prompt}
                      onChange={(e) => handleLyricsFormChange('custom_prompt', e.target.value)}
                      placeholder="Additional instructions for lyrics generation..."
                      className="form-textarea"
                      rows={3}
                    />
                  </div>
                </div>

                <button
                  onClick={generateLyricsOnly}
                  disabled={isGenerating || !lyricsForm.title.trim()}
                  className="generate-button"
                >
                  {isGenerating ? 'Generating...' : 'Generate Lyrics'}
                </button>
              </div>
            )}

            {activeTab === 'instrumental' && (
              <div className="form-section">
                <h3>Generate Instrumental</h3>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Track Title *</label>
                    <input
                      type="text"
                      value={instrumentalForm.title}
                      onChange={(e) => handleInstrumentalFormChange('title', e.target.value)}
                      placeholder="Enter track title..."
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Genre</label>
                    <select
                      value={instrumentalForm.genre}
                      onChange={(e) => handleInstrumentalFormChange('genre', e.target.value)}
                      className="form-select"
                    >
                      {GENRES.map(genre => (
                        <option key={genre} value={genre}>{genre}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Style</label>
                    <select
                      value={instrumentalForm.style}
                      onChange={(e) => handleInstrumentalFormChange('style', e.target.value)}
                      className="form-select"
                    >
                      {STYLES.map(style => (
                        <option key={style} value={style}>{style}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Key</label>
                    <select
                      value={instrumentalForm.key}
                      onChange={(e) => handleInstrumentalFormChange('key', e.target.value)}
                      className="form-select"
                    >
                      {keys.map(key => (
                        <option key={key} value={key}>{key}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Tempo (BPM)</label>
                    <input
                      type="number"
                      value={instrumentalForm.tempo}
                      onChange={(e) => handleInstrumentalFormChange('tempo', parseInt(e.target.value))}
                      min="60"
                      max="200"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Duration (seconds)</label>
                    <input
                      type="number"
                      value={instrumentalForm.duration}
                      onChange={(e) => handleInstrumentalFormChange('duration', parseInt(e.target.value))}
                      min="30"
                      max="600"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={instrumentalForm.include_audio}
                        onChange={(e) => handleInstrumentalFormChange('include_audio', e.target.checked)}
                      />
                      Generate Audio
                    </label>
                  </div>
                </div>

                <button
                  onClick={generateInstrumentalOnly}
                  disabled={isGenerating || !instrumentalForm.title.trim()}
                  className="generate-button"
                >
                  {isGenerating ? 'Generating...' : 'Generate Instrumental'}
                </button>
              </div>
            )}

            {/* Generation Progress */}
            {isGenerating && (
              <div className="progress-section">
                <div className="progress-bar">
                  <div className="progress-fill"></div>
                </div>
                <p className="progress-text">{generationProgress}</p>
              </div>
            )}
          </div>

          {/* Suggestions Panel */}
          <div className="suggestions-panel">
            <h3>AI Suggestions</h3>
            {suggestions && (
              <div className="suggestions-content">
                {suggestions.recommended_tempos.length > 0 && (
                  <div className="suggestion-group">
                    <h4>Recommended Tempos</h4>
                    <div className="suggestion-chips">
                      {suggestions.recommended_tempos.map(tempo => (
                        <button
                          key={tempo}
                          className="suggestion-chip"
                          onClick={() => applySuggestion('tempo', tempo)}
                        >
                          {tempo} BPM
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {suggestions.recommended_keys.length > 0 && (
                  <div className="suggestion-group">
                    <h4>Recommended Keys</h4>
                    <div className="suggestion-chips">
                      {suggestions.recommended_keys.map(key => (
                        <button
                          key={key}
                          className="suggestion-chip"
                          onClick={() => applySuggestion('key', key)}
                        >
                          {key}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {suggestions.recommended_styles.length > 0 && (
                  <div className="suggestion-group">
                    <h4>Recommended Styles</h4>
                    <div className="suggestion-chips">
                      {suggestions.recommended_styles.map(style => (
                        <button
                          key={style}
                          className="suggestion-chip"
                          onClick={() => applySuggestion('style', style)}
                        >
                          {style}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {suggestions.theme_suggestions.length > 0 && (
                  <div className="suggestion-group">
                    <h4>Theme Ideas</h4>
                    <div className="suggestion-chips">
                      {suggestions.theme_suggestions.map(theme => (
                        <button
                          key={theme}
                          className="suggestion-chip"
                          onClick={() => applySuggestion('theme', theme)}
                        >
                          {theme}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {(generatedSong || generatedLyrics || generatedInstrumental) && (
          <div className="results-section">
            <h3>Generation Results</h3>
            
            {generatedSong && (
              <div className="result-card">
                <div className="result-header">
                  <h4>{generatedSong.title}</h4>
                  <span className="result-genre">{generatedSong.genre}</span>
                </div>
                <div className="result-content">
                  {generatedSong.lyrics && (
                    <div className="lyrics-display">
                      <h5>Lyrics:</h5>
                      <pre className="lyrics-text">{generatedSong.lyrics}</pre>
                    </div>
                  )}
                  <div className="result-metadata">
                    <span>Duration: {formatDuration(generatedSong.duration || 0)}</span>
                    <span>Tempo: {generatedSong.tempo} BPM</span>
                    <span>Key: {generatedSong.key_signature}</span>
                  </div>
                  {generatedSong.audio_file_path && (
                    <div className="audio-player">
                      <audio controls>
                        <source src={generatedSong.audio_file_path} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}
                </div>
              </div>
            )}

            {generatedLyrics && (
              <div className="result-card">
                <div className="result-header">
                  <h4>Generated Lyrics</h4>
                </div>
                <div className="result-content">
                  <div className="lyrics-display">
                    <pre className="lyrics-text">{generatedLyrics.lyrics}</pre>
                  </div>
                  <div className="result-metadata">
                    <span>Word Count: {generatedLyrics.metadata?.word_count}</span>
                    <span>Est. Duration: {formatDuration(generatedLyrics.metadata?.estimated_duration || 0)}</span>
                  </div>
                </div>
              </div>
            )}

            {generatedInstrumental && (
              <div className="result-card">
                <div className="result-header">
                  <h4>{generatedInstrumental.title}</h4>
                  <span className="result-genre">{generatedInstrumental.genre}</span>
                </div>
                <div className="result-content">
                  <div className="result-metadata">
                    <span>Duration: {formatDuration(generatedInstrumental.duration || 0)}</span>
                    <span>Tempo: {generatedInstrumental.tempo} BPM</span>
                    <span>Key: {generatedInstrumental.key}</span>
                  </div>
                  {generatedInstrumental.audio_file_path && (
                    <div className="audio-player">
                      <audio controls>
                        <source src={generatedInstrumental.audio_file_path} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Recent Songs */}
        {recentSongs.length > 0 && (
          <div className="recent-songs-section">
            <h3>Recent Generations</h3>
            <div className="songs-grid">
              {recentSongs.map(song => (
                <div key={song.id} className="song-card">
                  <div className="song-header">
                    <h4>{song.title}</h4>
                    <span className="song-genre">{song.genre}</span>
                  </div>
                  <div className="song-metadata">
                    {song.duration && <span>{formatDuration(song.duration)}</span>}
                    {song.tempo && <span>{song.tempo} BPM</span>}
                    {song.is_generated && <span className="generated-badge">AI Generated</span>}
                  </div>
                  {song.audio_file_path && (
                    <div className="song-audio">
                      <audio controls>
                        <source src={song.audio_file_path} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
