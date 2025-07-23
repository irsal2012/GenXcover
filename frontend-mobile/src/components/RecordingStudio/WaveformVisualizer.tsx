import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import Svg, { Path, Defs, LinearGradient, Stop } from 'react-native-svg';

interface WaveformVisualizerProps {
  audioLevels: number[];
  isRecording: boolean;
  width: number;
  height: number;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  audioLevels,
  isRecording,
  width,
  height,
}) => {
  const animationValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (isRecording) {
      Animated.loop(
        Animated.timing(animationValue, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: false,
        })
      ).start();
    } else {
      animationValue.stopAnimation();
      animationValue.setValue(0);
    }
  }, [isRecording]);

  const generateWaveformPath = () => {
    if (audioLevels.length === 0) {
      return `M 0 ${height / 2} L ${width} ${height / 2}`;
    }

    const points = audioLevels.map((level, index) => {
      const x = (index / (audioLevels.length - 1)) * width;
      const y = height / 2 + (level - 50) * (height / 100);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    });

    return points.join(' ');
  };

  const generateBars = () => {
    const barCount = 50;
    const barWidth = width / barCount;
    const bars = [];

    for (let i = 0; i < barCount; i++) {
      const levelIndex = Math.floor((i / barCount) * audioLevels.length);
      const level = audioLevels[levelIndex] || 0;
      const barHeight = (level / 100) * height * 0.8;
      const x = i * barWidth;
      const y = (height - barHeight) / 2;

      bars.push(
        <Animated.View
          key={i}
          style={[
            styles.bar,
            {
              left: x,
              bottom: y,
              width: barWidth - 2,
              height: barHeight,
              backgroundColor: isRecording ? '#4CAF50' : '#666',
              opacity: animationValue.interpolate({
                inputRange: [0, 1],
                outputRange: [0.3, 1],
              }),
            },
          ]}
        />
      );
    }

    return bars;
  };

  return (
    <View style={[styles.container, { width, height }]}>
      <View style={styles.background}>
        {generateBars()}
      </View>
      
      {isRecording && (
        <View style={styles.overlay}>
          <Svg width={width} height={height}>
            <Defs>
              <LinearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <Stop offset="0%" stopColor="#4CAF50" stopOpacity="0.8" />
                <Stop offset="50%" stopColor="#8BC34A" stopOpacity="0.6" />
                <Stop offset="100%" stopColor="#CDDC39" stopOpacity="0.4" />
              </LinearGradient>
            </Defs>
            <Path
              d={generateWaveformPath()}
              stroke="url(#waveGradient)"
              strokeWidth="2"
              fill="none"
            />
          </Svg>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    overflow: 'hidden',
  },
  background: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  bar: {
    position: 'absolute',
    borderRadius: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
});

export default WaveformVisualizer;
