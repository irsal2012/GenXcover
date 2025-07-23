import { useState } from 'react';
import * as FileSystem from 'expo-file-system';
import { apiService } from '../services/api';

interface AudioAnalysisResult {
  duration: number;
  quality: 'low' | 'medium' | 'high';
  genre: string;
  tempo: number;
  energy: number;
  danceability: number;
  valence: number;
  popularityScore: number;
  recommendations: string[];
}

interface UseAudioAnalysisReturn {
  analyzeAudio: (audioUri: string) => Promise<AudioAnalysisResult>;
  isAnalyzing: boolean;
  error: string | null;
}

export const useAudioAnalysis = (): UseAudioAnalysisReturn => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeAudio = async (audioUri: string): Promise<AudioAnalysisResult> => {
    setIsAnalyzing(true);
    setError(null);

    try {
      // Get file info
      const fileInfo = await FileSystem.getInfoAsync(audioUri);
      if (!fileInfo.exists) {
        throw new Error('Audio file not found');
      }

      // Create FormData for upload
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/wav',
        name: 'recording.wav',
      } as any);

      // Upload and analyze audio
      const response = await apiService.post('/api/v1/songs/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const analysisData = response.data;

      // Process and format the analysis results
      const result: AudioAnalysisResult = {
        duration: analysisData.basic?.duration || 0,
        quality: determineQuality(analysisData),
        genre: analysisData.genre || 'unknown',
        tempo: analysisData.temporal?.tempo || 120,
        energy: analysisData.perceptual?.energy || 0.5,
        danceability: analysisData.perceptual?.danceability || 0.5,
        valence: analysisData.perceptual?.valence || 0.5,
        popularityScore: analysisData.commercial?.overall_viability_score || 0.5,
        recommendations: analysisData.commercial?.improvement_areas || [],
      };

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      
      // Return default analysis if API fails
      return {
        duration: 0,
        quality: 'medium',
        genre: 'unknown',
        tempo: 120,
        energy: 0.5,
        danceability: 0.5,
        valence: 0.5,
        popularityScore: 0.5,
        recommendations: ['Unable to analyze audio'],
      };
    } finally {
      setIsAnalyzing(false);
    }
  };

  const determineQuality = (analysisData: any): 'low' | 'medium' | 'high' => {
    const dynamicRange = analysisData.basic?.dynamic_range_db || 0;
    const peakLevel = analysisData.basic?.peak_amplitude || 0;
    
    if (dynamicRange > 12 && peakLevel < 0.95) {
      return 'high';
    } else if (dynamicRange > 6 && peakLevel < 0.98) {
      return 'medium';
    } else {
      return 'low';
    }
  };

  return {
    analyzeAudio,
    isAnalyzing,
    error,
  };
};
