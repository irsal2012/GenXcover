import axios, { AxiosResponse } from 'axios';
import {
  User,
  Song,
  SongCreate,
  SongGenerate,
  SongList,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  ApiError
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response: AxiosResponse<AuthTokens> = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/users/me');
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getProfile: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/users/me');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/users/me', userData);
    return response.data;
  },

  getUser: async (userId: number): Promise<User> => {
    const response: AxiosResponse<User> = await api.get(`/users/${userId}`);
    return response.data;
  },

  getUsers: async (skip = 0, limit = 100): Promise<User[]> => {
    const response: AxiosResponse<User[]> = await api.get('/users', {
      params: { skip, limit }
    });
    return response.data;
  },
};

// Songs API
export const songsAPI = {
  getSongs: async (params?: {
    skip?: number;
    limit?: number;
    genre?: string;
    creator_id?: number;
  }): Promise<SongList> => {
    const response: AxiosResponse<SongList> = await api.get('/songs', { params });
    return response.data;
  },

  getMySongs: async (skip = 0, limit = 20): Promise<Song[]> => {
    const response: AxiosResponse<Song[]> = await api.get('/songs/my-songs', {
      params: { skip, limit }
    });
    return response.data;
  },

  getSong: async (songId: number): Promise<Song> => {
    const response: AxiosResponse<Song> = await api.get(`/songs/${songId}`);
    return response.data;
  },

  createSong: async (songData: SongCreate): Promise<Song> => {
    const response: AxiosResponse<Song> = await api.post('/songs', songData);
    return response.data;
  },

  generateSong: async (songData: SongGenerate): Promise<Song> => {
    const response: AxiosResponse<Song> = await api.post('/songs/generate', songData);
    return response.data;
  },

  updateSong: async (songId: number, songData: Partial<Song>): Promise<Song> => {
    const response: AxiosResponse<Song> = await api.put(`/songs/${songId}`, songData);
    return response.data;
  },

  deleteSong: async (songId: number): Promise<void> => {
    await api.delete(`/songs/${songId}`);
  },
};

// File upload API
export const uploadAPI = {
  uploadAudio: async (file: File, songId?: number): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    if (songId) {
      formData.append('song_id', songId.toString());
    }

    const response: AxiosResponse<{ file_path: string }> = await api.post(
      '/upload/audio',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.file_path;
  },

  uploadImage: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<{ file_path: string }> = await api.post(
      '/upload/image',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.file_path;
  },
};

// Health check
export const healthAPI = {
  check: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
