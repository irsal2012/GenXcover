import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
  Alert,
  Platform,
} from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import WaveformVisualizer from './WaveformVisualizer';
import EffectsPanel from './EffectsPanel';
import { useRecording } from '../../hooks/useRecording';
import { useAudioAnalysis } from '../../hooks/useAudioAnalysis';

const { width, height } = Dimensions.get('window');

interface MobileRecorderProps {
  onRecordingComplete: (audioUri: string, analysis: any) => void;
  onClose: () => void;
}

const MobileRecorder: React.FC<MobileRecorderProps> = ({
  onRecordingComplete,
  onClose,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioLevels, setAudioLevels] = useState<number[]>([]);
  const [selectedEffect, setSelectedEffect] = useState<string | null>(null);
  const [showEffects, setShowEffects] = useState(false);

  const recordingAnimation = useRef(new Animated.Value(0)).current;
  const pulseAnimation = useRef(new Animated.Value(1)).current;
  const waveformData = useRef<number[]>([]);

  const {
    recording,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    getRecordingUri,
  } = useRecording();

  const { analyzeAudio, isAnalyzing } = useAudioAnalysis();

  useEffect(() => {
    if (isRecording && !isPaused) {
      startPulseAnimation();
      startRecordingTimer();
    } else {
      stopPulseAnimation();
    }

    return () => {
      stopPulseAnimation();
    };
  }, [isRecording, isPaused]);

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnimation, {
          toValue: 1.2,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnimation, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopPulseAnimation = () => {
    pulseAnimation.stopAnimation();
    Animated.timing(pulseAnimation, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }).start();
  };

  const startRecordingTimer = () => {
    const interval = setInterval(() => {
      if (isRecording && !isPaused) {
        setRecordingDuration(prev => prev + 1);
        // Simulate audio level data
        const level = Math.random() * 100;
        setAudioLevels(prev => [...prev.slice(-50), level]);
        waveformData.current.push(level);
      }
    }, 100);

    return () => clearInterval(interval);
  };

  const handleStartRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Please grant microphone permission to record audio.');
        return;
      }

      await startRecording();
      setIsRecording(true);
      setRecordingDuration(0);
      setAudioLevels([]);
      waveformData.current = [];

      Animated.timing(recordingAnimation, {
        toValue: 1,
        duration: 300,
        useNativeDriver: false,
      }).start();
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please try again.');
    }
  };

  const handleStopRecording = async () => {
    try {
      const uri = await stopRecording();
      setIsRecording(false);
      setIsPaused(false);

      Animated.timing(recordingAnimation, {
        toValue: 0,
        duration: 300,
        useNativeDriver: false,
      }).start();

      if (uri) {
        // Analyze the recorded audio
        const analysis = await analyzeAudio(uri);
        onRecordingComplete(uri, analysis);
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to stop recording. Please try again.');
    }
  };

  const handlePauseResume = async () => {
    try {
      if (isPaused) {
        await resumeRecording();
        setIsPaused(false);
      } else {
        await pauseRecording();
        setIsPaused(true);
      }
    } catch (error) {
      console.error('Failed to pause/resume recording:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getRecordingButtonColor = () => {
    if (isRecording && !isPaused) return '#FF4444';
    if (isPaused) return '#FFA500';
    return '#4CAF50';
  };

  const getRecordingButtonIcon = () => {
    if (isRecording && !isPaused) return 'stop';
    if (isPaused) return 'play';
    return 'mic';
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#16213e', '#0f3460']}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Ionicons name="close" size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Mobile Studio</Text>
          <TouchableOpacity
            onPress={() => setShowEffects(!showEffects)}
            style={styles.effectsButton}
          >
            <Ionicons name="options" size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Recording Duration */}
        <View style={styles.durationContainer}>
          <Text style={styles.durationText}>
            {formatDuration(recordingDuration)}
          </Text>
          {isRecording && (
            <View style={styles.recordingIndicator}>
              <Animated.View
                style={[
                  styles.recordingDot,
                  {
                    transform: [{ scale: pulseAnimation }],
                  },
                ]}
              />
              <Text style={styles.recordingText}>REC</Text>
            </View>
          )}
        </View>

        {/* Waveform Visualizer */}
        <View style={styles.waveformContainer}>
          <WaveformVisualizer
            audioLevels={audioLevels}
            isRecording={isRecording}
            width={width - 40}
            height={120}
          />
        </View>

        {/* Audio Level Meter */}
        <View style={styles.levelMeterContainer}>
          <Text style={styles.levelLabel}>Input Level</Text>
          <View style={styles.levelMeter}>
            <Animated.View
              style={[
                styles.levelBar,
                {
                  width: recordingAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', `${Math.max(...audioLevels.slice(-5)) || 0}%`],
                  }),
                },
              ]}
            />
          </View>
        </View>

        {/* Effects Panel */}
        {showEffects && (
          <EffectsPanel
            selectedEffect={selectedEffect}
            onEffectSelect={setSelectedEffect}
            onClose={() => setShowEffects(false)}
          />
        )}

        {/* Control Buttons */}
        <View style={styles.controlsContainer}>
          {isRecording && (
            <TouchableOpacity
              onPress={handlePauseResume}
              style={[styles.controlButton, styles.pauseButton]}
            >
              <Ionicons
                name={isPaused ? 'play' : 'pause'}
                size={24}
                color="#fff"
              />
            </TouchableOpacity>
          )}

          <Animated.View
            style={[
              styles.recordButtonContainer,
              {
                transform: [{ scale: pulseAnimation }],
              },
            ]}
          >
            <TouchableOpacity
              onPress={isRecording ? handleStopRecording : handleStartRecording}
              style={[
                styles.recordButton,
                { backgroundColor: getRecordingButtonColor() },
              ]}
              disabled={isAnalyzing}
            >
              <Ionicons
                name={getRecordingButtonIcon()}
                size={32}
                color="#fff"
              />
            </TouchableOpacity>
          </Animated.View>

          {isRecording && (
            <TouchableOpacity
              onPress={() => {/* Add bookmark functionality */}}
              style={[styles.controlButton, styles.bookmarkButton]}
            >
              <Ionicons name="bookmark" size={24} color="#fff" />
            </TouchableOpacity>
          )}
        </View>

        {/* Recording Stats */}
        {isRecording && (
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Quality</Text>
              <Text style={styles.statValue}>HD</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Format</Text>
              <Text style={styles.statValue}>WAV</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Size</Text>
              <Text style={styles.statValue}>
                {((recordingDuration * 44100 * 2) / 1024 / 1024).toFixed(1)}MB
              </Text>
            </View>
          </View>
        )}

        {/* Analysis Loading */}
        {isAnalyzing && (
          <View style={styles.analysisContainer}>
            <Text style={styles.analysisText}>Analyzing audio...</Text>
            <Animated.View style={styles.analysisSpinner} />
          </View>
        )}
      </LinearGradient>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    paddingBottom: 20,
  },
  closeButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  effectsButton: {
    padding: 8,
  },
  durationContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  durationText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  recordingDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#FF4444',
    marginRight: 8,
  },
  recordingText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FF4444',
  },
  waveformContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  levelMeterContainer: {
    paddingHorizontal: 20,
    marginBottom: 30,
  },
  levelLabel: {
    fontSize: 14,
    color: '#fff',
    marginBottom: 8,
  },
  levelMeter: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  levelBar: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 4,
  },
  controlsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 30,
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 20,
  },
  pauseButton: {
    backgroundColor: '#FFA500',
  },
  bookmarkButton: {
    backgroundColor: '#2196F3',
  },
  recordButtonContainer: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  recordButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  analysisContainer: {
    alignItems: 'center',
    padding: 20,
  },
  analysisText: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 10,
  },
  analysisSpinner: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#4CAF50',
  },
});

export default MobileRecorder;
