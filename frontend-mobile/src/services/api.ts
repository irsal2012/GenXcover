import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// API Configuration
const API_BASE_URL = __DEV__ 
  ? Platform.OS === 'ios' 
    ? 'http://localhost:8000' 
    : 'http://10.0.2.2:8000'
  : 'https://api.genxcover.com';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        try {
          const token = await AsyncStorage.getItem('authToken');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.error('Error getting auth token:', error);
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await AsyncStorage.removeItem('authToken');
          await AsyncStorage.removeItem('user');
          // Navigate to login screen
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<any> {
    const response = await this.api.post('/api/v1/auth/login', {
      username: email,
      password,
    });
    
    if (response.data.access_token) {
      await AsyncStorage.setItem('authToken', response.data.access_token);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  }

  async register(userData: {
    email: string;
    password: string;
    full_name: string;
  }): Promise<any> {
    const response = await this.api.post('/api/v1/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('user');
  }

  // Songs
  async getSongs(): Promise<any> {
    const response = await this.api.get('/api/v1/songs/');
    return response.data;
  }

  async createSong(songData: any): Promise<any> {
    const response = await this.api.post('/api/v1/songs/', songData);
    return response.data;
  }

  async getSong(songId: string): Promise<any> {
    const response = await this.api.get(`/api/v1/songs/${songId}`);
    return response.data;
  }

  async updateSong(songId: string, songData: any): Promise<any> {
    const response = await this.api.put(`/api/v1/songs/${songId}`, songData);
    return response.data;
  }

  async deleteSong(songId: string): Promise<void> {
    await this.api.delete(`/api/v1/songs/${songId}`);
  }

  // Music Generation
  async generateMusic(params: {
    genre: string;
    style: string;
    tempo: number;
    key: string;
    duration: number;
    voice_type?: string;
    lyrics?: string;
  }): Promise<any> {
    const response = await this.api.post('/api/v1/songs/generate', params);
    return response.data;
  }

  async generateLyrics(params: {
    theme: string;
    genre: string;
    mood: string;
    length: string;
  }): Promise<any> {
    const response = await this.api.post('/api/v1/songs/generate-lyrics', params);
    return response.data;
  }

  // Audio Analysis
  async analyzeAudio(audioFile: FormData): Promise<any> {
    const response = await this.api.post('/api/v1/songs/analyze', audioFile, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // Extended timeout for audio processing
    });
    return response.data;
  }

  // Popularity Prediction
  async predictPopularity(params: {
    audio_file?: FormData;
    song_id?: string;
    lyrics?: string;
    genre: string;
    artist_profile?: any;
  }): Promise<any> {
    const response = await this.api.post('/api/v1/songs/predict-popularity', params, {
      headers: params.audio_file ? { 'Content-Type': 'multipart/form-data' } : {},
      timeout: 90000, // Extended timeout for AI analysis
    });
    return response.data;
  }

  // Recording Studio
  async createRecordingSession(sessionData: {
    name: string;
    settings?: any;
  }): Promise<any> {
    const response = await this.api.post('/api/v1/recording/sessions', sessionData);
    return response.data;
  }

  async uploadRecording(sessionId: string, audioFile: FormData): Promise<any> {
    const response = await this.api.post(
      `/api/v1/recording/sessions/${sessionId}/upload`,
      audioFile,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // Extended timeout for large audio files
      }
    );
    return response.data;
  }

  async getRecordingSessions(): Promise<any> {
    const response = await this.api.get('/api/v1/recording/sessions');
    return response.data;
  }

  async getRecordingSession(sessionId: string): Promise<any> {
    const response = await this.api.get(`/api/v1/recording/sessions/${sessionId}`);
    return response.data;
  }

  // User Profile
  async getUserProfile(): Promise<any> {
    const response = await this.api.get('/api/v1/users/me');
    return response.data;
  }

  async updateUserProfile(profileData: any): Promise<any> {
    const response = await this.api.put('/api/v1/users/me', profileData);
    return response.data;
  }

  // Generic HTTP methods
  async get(url: string, config?: any): Promise<AxiosResponse> {
    return this.api.get(url, config);
  }

  async post(url: string, data?: any, config?: any): Promise<AxiosResponse> {
    return this.api.post(url, data, config);
  }

  async put(url: string, data?: any, config?: any): Promise<AxiosResponse> {
    return this.api.put(url, data, config);
  }

  async delete(url: string, config?: any): Promise<AxiosResponse> {
    return this.api.delete(url, config);
  }

  // Utility methods
  async checkConnection(): Promise<boolean> {
    try {
      await this.api.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  async uploadFile(
    url: string,
    file: any,
    onProgress?: (progress: number) => void
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress(progress);
        }
      },
    });
  }
}

export const apiService = new ApiService();
export default apiService;
