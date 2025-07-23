export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  bio?: string;
  profile_picture?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Song {
  id: number;
  title: string;
  genre: string;
  style?: string;
  theme?: string;
  voice_type?: string;
  lyrics?: string;
  audio_file_path?: string;
  midi_file_path?: string;
  cover_image_path?: string;
  duration?: number;
  tempo?: number;
  key_signature?: string;
  time_signature?: string;
  audio_features?: Record<string, any>;
  generation_params?: Record<string, any>;
  is_generated: boolean;
  is_public: boolean;
  creator_id: number;
  created_at: string;
  updated_at?: string;
}

export interface SongCreate {
  title: string;
  genre: string;
  style?: string;
  theme?: string;
  voice_type?: string;
  lyrics?: string;
  generation_params?: Record<string, any>;
}

export interface SongGenerate {
  title: string;
  genre: string;
  style?: string;
  theme?: string;
  voice_type?: string;
  custom_prompt?: string;
  include_audio: boolean;
  include_midi: boolean;
}

export interface Recording {
  id: number;
  title: string;
  description?: string;
  audio_file_path: string;
  waveform_data_path?: string;
  duration?: number;
  sample_rate?: number;
  channels?: number;
  bit_depth?: number;
  effects_applied?: Record<string, any>;
  recording_settings?: Record<string, any>;
  track_number: number;
  is_master_track: boolean;
  parent_recording_id?: number;
  is_processed: boolean;
  is_public: boolean;
  user_id: number;
  song_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface PopularityPrediction {
  id: number;
  popularity_score: number;
  confidence_score: number;
  audio_analysis?: Record<string, any>;
  lyrics_analysis?: Record<string, any>;
  market_analysis?: Record<string, any>;
  genre_fit_score?: number;
  trend_alignment_score?: number;
  catchiness_score?: number;
  commercial_appeal_score?: number;
  improvement_suggestions?: Record<string, any>;
  target_demographics?: Record<string, any>;
  optimal_release_timing?: Record<string, any>;
  model_version: string;
  analysis_timestamp: string;
  song_id: number;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  bio?: string;
}

export interface ApiError {
  detail: string;
}

export interface SongList {
  songs: Song[];
  total: number;
  page: number;
  per_page: number;
}

// Audio-related types
export interface AudioEffect {
  type: string;
  parameters: Record<string, any>;
}

export interface RecordingSettings {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  effects: AudioEffect[];
}

// Music generation types
export const GENRES = [
  'Pop', 'Rock', 'Hip Hop', 'R&B', 'Country', 'Electronic', 'Jazz', 'Classical',
  'Folk', 'Blues', 'Reggae', 'Punk', 'Metal', 'Alternative', 'Indie'
] as const;

export const VOICE_TYPES = [
  'Male', 'Female', 'Child', 'Robotic', 'Choir', 'Instrumental'
] as const;

export const STYLES = [
  'Upbeat', 'Melancholic', 'Energetic', 'Calm', 'Dramatic', 'Romantic',
  'Aggressive', 'Dreamy', 'Nostalgic', 'Futuristic'
] as const;

export type Genre = typeof GENRES[number];
export type VoiceType = typeof VOICE_TYPES[number];
export type Style = typeof STYLES[number];
