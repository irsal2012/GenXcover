import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Song, SongGenerate } from '../../types';
import { songsAPI } from '../../services/api';

interface SongsState {
  songs: Song[];
  mySongs: Song[];
  currentSong: Song | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
  pagination: {
    total: number;
    page: number;
    per_page: number;
  };
}

const initialState: SongsState = {
  songs: [],
  mySongs: [],
  currentSong: null,
  isLoading: false,
  isGenerating: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    per_page: 20,
  },
};

// Async thunks
export const fetchSongs = createAsyncThunk(
  'songs/fetchSongs',
  async (params: {
    skip?: number;
    limit?: number;
    genre?: string;
    creator_id?: number;
  } | undefined, { rejectWithValue }) => {
    try {
      const response = await songsAPI.getSongs(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch songs');
    }
  }
);

export const fetchMySongs = createAsyncThunk(
  'songs/fetchMySongs',
  async (params: { skip?: number; limit?: number } | undefined, { rejectWithValue }) => {
    try {
      const songs = await songsAPI.getMySongs(params?.skip, params?.limit);
      return songs;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch my songs');
    }
  }
);

export const fetchSong = createAsyncThunk(
  'songs/fetchSong',
  async (songId: number, { rejectWithValue }) => {
    try {
      const song = await songsAPI.getSong(songId);
      return song;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch song');
    }
  }
);

export const generateSong = createAsyncThunk(
  'songs/generateSong',
  async (songData: SongGenerate, { rejectWithValue }) => {
    try {
      const song = await songsAPI.generateSong(songData);
      return song;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate song');
    }
  }
);

export const deleteSong = createAsyncThunk(
  'songs/deleteSong',
  async (songId: number, { rejectWithValue }) => {
    try {
      await songsAPI.deleteSong(songId);
      return songId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete song');
    }
  }
);

const songsSlice = createSlice({
  name: 'songs',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentSong: (state, action: PayloadAction<Song | null>) => {
      state.currentSong = action.payload;
    },
    updateSong: (state, action: PayloadAction<Song>) => {
      const updatedSong = action.payload;
      
      // Update in songs array
      const songIndex = state.songs.findIndex(song => song.id === updatedSong.id);
      if (songIndex !== -1) {
        state.songs[songIndex] = updatedSong;
      }
      
      // Update in mySongs array
      const mySongIndex = state.mySongs.findIndex(song => song.id === updatedSong.id);
      if (mySongIndex !== -1) {
        state.mySongs[mySongIndex] = updatedSong;
      }
      
      // Update current song if it's the same
      if (state.currentSong?.id === updatedSong.id) {
        state.currentSong = updatedSong;
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch songs
    builder
      .addCase(fetchSongs.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSongs.fulfilled, (state, action) => {
        state.isLoading = false;
        state.songs = action.payload.songs;
        state.pagination = {
          total: action.payload.total,
          page: action.payload.page,
          per_page: action.payload.per_page,
        };
      })
      .addCase(fetchSongs.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch my songs
    builder
      .addCase(fetchMySongs.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMySongs.fulfilled, (state, action) => {
        state.isLoading = false;
        state.mySongs = action.payload;
      })
      .addCase(fetchMySongs.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch single song
    builder
      .addCase(fetchSong.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSong.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentSong = action.payload;
      })
      .addCase(fetchSong.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Generate song
    builder
      .addCase(generateSong.pending, (state) => {
        state.isGenerating = true;
        state.error = null;
      })
      .addCase(generateSong.fulfilled, (state, action) => {
        state.isGenerating = false;
        state.mySongs.unshift(action.payload);
        state.currentSong = action.payload;
      })
      .addCase(generateSong.rejected, (state, action) => {
        state.isGenerating = false;
        state.error = action.payload as string;
      });

    // Delete song
    builder
      .addCase(deleteSong.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteSong.fulfilled, (state, action) => {
        state.isLoading = false;
        const songId = action.payload;
        state.songs = state.songs.filter(song => song.id !== songId);
        state.mySongs = state.mySongs.filter(song => song.id !== songId);
        if (state.currentSong?.id === songId) {
          state.currentSong = null;
        }
      })
      .addCase(deleteSong.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setCurrentSong, updateSong } = songsSlice.actions;
export default songsSlice.reducer;
