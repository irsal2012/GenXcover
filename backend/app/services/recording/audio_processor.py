import numpy as np
import scipy.signal as signal
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime


class AudioProcessor:
    """Advanced audio processing service for recording studio features"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bit_depth = 16
        self.max_amplitude = 2**(self.bit_depth - 1) - 1
        
        # Initialize effect processors
        self.effects = {
            'reverb': self._create_reverb_processor(),
            'delay': self._create_delay_processor(),
            'chorus': self._create_chorus_processor(),
            'compressor': self._create_compressor_processor(),
            'eq': self._create_eq_processor(),
            'distortion': self._create_distortion_processor(),
            'auto_tune': self._create_auto_tune_processor(),
            'noise_gate': self._create_noise_gate_processor()
        }
    
    def _create_reverb_processor(self) -> Dict[str, Any]:
        """Create reverb effect processor"""
        return {
            'type': 'reverb',
            'parameters': {
                'room_size': 0.5,      # 0.0 - 1.0
                'damping': 0.5,        # 0.0 - 1.0
                'wet_level': 0.3,      # 0.0 - 1.0
                'dry_level': 0.7,      # 0.0 - 1.0
                'width': 1.0,          # 0.0 - 1.0
                'freeze_mode': False
            },
            'delay_lines': self._create_reverb_delay_lines()
        }
    
    def _create_delay_processor(self) -> Dict[str, Any]:
        """Create delay effect processor"""
        return {
            'type': 'delay',
            'parameters': {
                'delay_time': 0.25,    # seconds
                'feedback': 0.4,       # 0.0 - 0.95
                'wet_level': 0.3,      # 0.0 - 1.0
                'dry_level': 0.7,      # 0.0 - 1.0
                'high_cut': 8000,      # Hz
                'low_cut': 100         # Hz
            }
        }
    
    def _create_chorus_processor(self) -> Dict[str, Any]:
        """Create chorus effect processor"""
        return {
            'type': 'chorus',
            'parameters': {
                'rate': 1.5,           # Hz
                'depth': 0.02,         # 0.0 - 1.0
                'delay': 0.007,        # seconds
                'feedback': 0.1,       # 0.0 - 0.95
                'wet_level': 0.5       # 0.0 - 1.0
            }
        }
    
    def _create_compressor_processor(self) -> Dict[str, Any]:
        """Create compressor effect processor"""
        return {
            'type': 'compressor',
            'parameters': {
                'threshold': -20,      # dB
                'ratio': 4.0,          # 1.0 - 20.0
                'attack': 0.003,       # seconds
                'release': 0.1,        # seconds
                'knee': 2.0,           # dB
                'makeup_gain': 0       # dB
            }
        }
    
    def _create_eq_processor(self) -> Dict[str, Any]:
        """Create equalizer effect processor"""
        return {
            'type': 'eq',
            'parameters': {
                'low_gain': 0,         # dB (-20 to +20)
                'low_freq': 100,       # Hz
                'mid_gain': 0,         # dB
                'mid_freq': 1000,      # Hz
                'mid_q': 1.0,          # 0.1 - 10.0
                'high_gain': 0,        # dB
                'high_freq': 10000     # Hz
            }
        }
    
    def _create_distortion_processor(self) -> Dict[str, Any]:
        """Create distortion effect processor"""
        return {
            'type': 'distortion',
            'parameters': {
                'drive': 0.5,          # 0.0 - 1.0
                'tone': 0.5,           # 0.0 - 1.0
                'level': 0.5,          # 0.0 - 1.0
                'type': 'overdrive'    # 'overdrive', 'fuzz', 'distortion'
            }
        }
    
    def _create_auto_tune_processor(self) -> Dict[str, Any]:
        """Create auto-tune effect processor"""
        return {
            'type': 'auto_tune',
            'parameters': {
                'key': 'C',            # Musical key
                'scale': 'major',      # 'major', 'minor', 'chromatic'
                'strength': 0.8,       # 0.0 - 1.0
                'speed': 0.1,          # 0.01 - 1.0
                'humanize': 0.1        # 0.0 - 1.0
            }
        }
    
    def _create_noise_gate_processor(self) -> Dict[str, Any]:
        """Create noise gate effect processor"""
        return {
            'type': 'noise_gate',
            'parameters': {
                'threshold': -40,      # dB
                'ratio': 10.0,         # 1.0 - inf
                'attack': 0.001,       # seconds
                'hold': 0.01,          # seconds
                'release': 0.1         # seconds
            }
        }
    
    def _create_reverb_delay_lines(self) -> List[Dict[str, float]]:
        """Create delay lines for reverb algorithm"""
        # Schroeder reverb delay line lengths (in samples)
        comb_delays = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617]
        allpass_delays = [556, 441, 341, 225]
        
        delay_lines = []
        
        # Comb filters
        for delay in comb_delays:
            delay_lines.append({
                'type': 'comb',
                'delay_samples': delay,
                'feedback': 0.84,
                'buffer': np.zeros(delay)
            })
        
        # Allpass filters
        for delay in allpass_delays:
            delay_lines.append({
                'type': 'allpass',
                'delay_samples': delay,
                'feedback': 0.7,
                'buffer': np.zeros(delay)
            })
        
        return delay_lines
    
    async def apply_effect(
        self,
        audio: np.ndarray,
        effect_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Apply a single effect to audio"""
        
        if effect_name not in self.effects:
            raise ValueError(f"Unknown effect: {effect_name}")
        
        effect = self.effects[effect_name].copy()
        
        # Update parameters if provided
        if parameters:
            effect['parameters'].update(parameters)
        
        # Apply the effect
        if effect_name == 'reverb':
            return self._apply_reverb(audio, effect)
        elif effect_name == 'delay':
            return self._apply_delay(audio, effect)
        elif effect_name == 'chorus':
            return self._apply_chorus(audio, effect)
        elif effect_name == 'compressor':
            return self._apply_compressor(audio, effect)
        elif effect_name == 'eq':
            return self._apply_eq(audio, effect)
        elif effect_name == 'distortion':
            return self._apply_distortion(audio, effect)
        elif effect_name == 'auto_tune':
            return self._apply_auto_tune(audio, effect)
        elif effect_name == 'noise_gate':
            return self._apply_noise_gate(audio, effect)
        else:
            return audio
    
    async def apply_effect_chain(
        self,
        audio: np.ndarray,
        effect_chain: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Apply a chain of effects to audio"""
        
        processed_audio = audio.copy()
        
        for effect_config in effect_chain:
            effect_name = effect_config.get('name')
            parameters = effect_config.get('parameters', {})
            
            if effect_name:
                processed_audio = await self.apply_effect(
                    processed_audio, effect_name, parameters
                )
        
        return processed_audio
    
    def _apply_reverb(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply reverb effect using Schroeder algorithm"""
        params = effect['parameters']
        delay_lines = effect['delay_lines']
        
        output = np.zeros_like(audio)
        
        # Process through comb filters
        comb_output = np.zeros_like(audio)
        for delay_line in delay_lines:
            if delay_line['type'] == 'comb':
                comb_out = self._process_comb_filter(audio, delay_line)
                comb_output += comb_out
        
        # Process through allpass filters
        allpass_input = comb_output
        for delay_line in delay_lines:
            if delay_line['type'] == 'allpass':
                allpass_input = self._process_allpass_filter(allpass_input, delay_line)
        
        # Mix wet and dry signals
        wet_level = params['wet_level']
        dry_level = params['dry_level']
        
        output = dry_level * audio + wet_level * allpass_input
        
        return output
    
    def _process_comb_filter(self, audio: np.ndarray, delay_line: Dict[str, Any]) -> np.ndarray:
        """Process audio through comb filter"""
        delay_samples = delay_line['delay_samples']
        feedback = delay_line['feedback']
        buffer = delay_line['buffer']
        
        output = np.zeros_like(audio)
        buffer_index = 0
        
        for i, sample in enumerate(audio):
            # Get delayed sample
            delayed_sample = buffer[buffer_index]
            
            # Calculate output
            output[i] = delayed_sample
            
            # Update buffer with input + feedback
            buffer[buffer_index] = sample + feedback * delayed_sample
            
            # Update buffer index
            buffer_index = (buffer_index + 1) % delay_samples
        
        return output
    
    def _process_allpass_filter(self, audio: np.ndarray, delay_line: Dict[str, Any]) -> np.ndarray:
        """Process audio through allpass filter"""
        delay_samples = delay_line['delay_samples']
        feedback = delay_line['feedback']
        buffer = delay_line['buffer']
        
        output = np.zeros_like(audio)
        buffer_index = 0
        
        for i, sample in enumerate(audio):
            # Get delayed sample
            delayed_sample = buffer[buffer_index]
            
            # Calculate output (allpass formula)
            output[i] = -feedback * sample + delayed_sample
            
            # Update buffer
            buffer[buffer_index] = sample + feedback * delayed_sample
            
            # Update buffer index
            buffer_index = (buffer_index + 1) % delay_samples
        
        return output
    
    def _apply_delay(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply delay effect"""
        params = effect['parameters']
        
        delay_samples = int(params['delay_time'] * self.sample_rate)
        feedback = params['feedback']
        wet_level = params['wet_level']
        dry_level = params['dry_level']
        
        # Create delay buffer
        delay_buffer = np.zeros(delay_samples)
        output = np.zeros_like(audio)
        buffer_index = 0
        
        for i, sample in enumerate(audio):
            # Get delayed sample
            delayed_sample = delay_buffer[buffer_index]
            
            # Calculate output
            output[i] = dry_level * sample + wet_level * delayed_sample
            
            # Update delay buffer with input + feedback
            delay_buffer[buffer_index] = sample + feedback * delayed_sample
            
            # Update buffer index
            buffer_index = (buffer_index + 1) % delay_samples
        
        return output
    
    def _apply_chorus(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply chorus effect"""
        params = effect['parameters']
        
        rate = params['rate']
        depth = params['depth']
        delay = params['delay']
        feedback = params['feedback']
        wet_level = params['wet_level']
        
        # Create modulated delay
        base_delay_samples = int(delay * self.sample_rate)
        max_delay_samples = base_delay_samples + int(depth * self.sample_rate)
        
        delay_buffer = np.zeros(max_delay_samples)
        output = np.zeros_like(audio)
        buffer_index = 0
        
        for i, sample in enumerate(audio):
            # Calculate modulated delay
            lfo = np.sin(2 * np.pi * rate * i / self.sample_rate)
            mod_delay = base_delay_samples + int(depth * self.sample_rate * lfo * 0.5)
            
            # Get delayed sample
            delay_index = (buffer_index - mod_delay) % max_delay_samples
            delayed_sample = delay_buffer[delay_index]
            
            # Calculate output
            output[i] = sample + wet_level * delayed_sample
            
            # Update delay buffer
            delay_buffer[buffer_index] = sample + feedback * delayed_sample
            
            # Update buffer index
            buffer_index = (buffer_index + 1) % max_delay_samples
        
        return output
    
    def _apply_compressor(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply compressor effect"""
        params = effect['parameters']
        
        threshold = 10**(params['threshold'] / 20)  # Convert dB to linear
        ratio = params['ratio']
        attack = params['attack']
        release = params['release']
        makeup_gain = 10**(params['makeup_gain'] / 20)
        
        # Calculate attack and release coefficients
        attack_coeff = np.exp(-1 / (attack * self.sample_rate))
        release_coeff = np.exp(-1 / (release * self.sample_rate))
        
        output = np.zeros_like(audio)
        envelope = 0.0
        
        for i, sample in enumerate(audio):
            # Calculate input level
            input_level = abs(sample)
            
            # Update envelope follower
            if input_level > envelope:
                envelope = attack_coeff * envelope + (1 - attack_coeff) * input_level
            else:
                envelope = release_coeff * envelope + (1 - release_coeff) * input_level
            
            # Calculate gain reduction
            if envelope > threshold:
                gain_reduction = threshold + (envelope - threshold) / ratio
                gain_reduction = gain_reduction / envelope
            else:
                gain_reduction = 1.0
            
            # Apply compression and makeup gain
            output[i] = sample * gain_reduction * makeup_gain
        
        return output
    
    def _apply_eq(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply 3-band equalizer"""
        params = effect['parameters']
        
        # Design filters
        nyquist = self.sample_rate / 2
        
        # Low shelf filter
        low_freq = params['low_freq'] / nyquist
        low_gain = 10**(params['low_gain'] / 20)
        b_low, a_low = signal.butter(2, low_freq, btype='low')
        
        # High shelf filter
        high_freq = params['high_freq'] / nyquist
        high_gain = 10**(params['high_gain'] / 20)
        b_high, a_high = signal.butter(2, high_freq, btype='high')
        
        # Mid peaking filter (simplified)
        mid_gain = 10**(params['mid_gain'] / 20)
        
        # Apply filters
        low_filtered = signal.filtfilt(b_low, a_low, audio) * (low_gain - 1)
        high_filtered = signal.filtfilt(b_high, a_high, audio) * (high_gain - 1)
        
        # Combine
        output = audio + low_filtered + high_filtered
        output = output * mid_gain  # Simplified mid-band gain
        
        return output
    
    def _apply_distortion(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply distortion effect"""
        params = effect['parameters']
        
        drive = params['drive']
        tone = params['tone']
        level = params['level']
        dist_type = params['type']
        
        # Apply drive
        driven = audio * (1 + drive * 10)
        
        # Apply distortion curve
        if dist_type == 'overdrive':
            # Soft clipping
            output = np.tanh(driven)
        elif dist_type == 'fuzz':
            # Hard clipping with asymmetry
            output = np.clip(driven, -0.7, 1.0)
        else:  # distortion
            # Sigmoid distortion
            output = 2 / (1 + np.exp(-driven)) - 1
        
        # Simple tone control (high-frequency rolloff)
        if tone < 0.5:
            # Low-pass filter for darker tone
            cutoff = 2000 + tone * 6000
            nyquist = self.sample_rate / 2
            b, a = signal.butter(2, cutoff / nyquist, btype='low')
            output = signal.filtfilt(b, a, output)
        
        # Apply output level
        output = output * level
        
        return output
    
    def _apply_auto_tune(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply auto-tune effect (simplified pitch correction)"""
        params = effect['parameters']
        
        # This is a very simplified auto-tune implementation
        # In production, you'd use more sophisticated pitch detection and correction
        
        strength = params['strength']
        
        # Simple pitch shifting using time-domain approach
        # This is a placeholder - real auto-tune requires complex pitch detection
        
        # Apply subtle pitch modulation to simulate auto-tune effect
        modulation_rate = 0.1  # Hz
        modulation_depth = 0.02 * strength
        
        output = np.zeros_like(audio)
        for i in range(len(audio)):
            mod = np.sin(2 * np.pi * modulation_rate * i / self.sample_rate)
            pitch_shift = 1 + modulation_depth * mod
            
            # Simple interpolation for pitch shifting (very basic)
            if i > 0:
                output[i] = audio[int(i / pitch_shift)] if int(i / pitch_shift) < len(audio) else 0
            else:
                output[i] = audio[i]
        
        # Mix with original signal
        output = (1 - strength) * audio + strength * output
        
        return output
    
    def _apply_noise_gate(self, audio: np.ndarray, effect: Dict[str, Any]) -> np.ndarray:
        """Apply noise gate effect"""
        params = effect['parameters']
        
        threshold = 10**(params['threshold'] / 20)  # Convert dB to linear
        ratio = params['ratio']
        attack = params['attack']
        hold = params['hold']
        release = params['release']
        
        # Calculate coefficients
        attack_coeff = np.exp(-1 / (attack * self.sample_rate))
        release_coeff = np.exp(-1 / (release * self.sample_rate))
        hold_samples = int(hold * self.sample_rate)
        
        output = np.zeros_like(audio)
        envelope = 0.0
        hold_counter = 0
        gate_open = False
        
        for i, sample in enumerate(audio):
            # Calculate input level
            input_level = abs(sample)
            
            # Update envelope
            if input_level > envelope:
                envelope = attack_coeff * envelope + (1 - attack_coeff) * input_level
            else:
                envelope = release_coeff * envelope + (1 - release_coeff) * input_level
            
            # Gate logic
            if envelope > threshold:
                gate_open = True
                hold_counter = hold_samples
            elif hold_counter > 0:
                hold_counter -= 1
            else:
                gate_open = False
            
            # Calculate gain
            if gate_open:
                gain = 1.0
            else:
                # Apply ratio for gating
                gain = min(1.0, envelope / threshold * ratio)
            
            output[i] = sample * gain
        
        return output
    
    async def analyze_audio(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze audio for various characteristics"""
        
        # Basic statistics
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
        
        # Frequency analysis
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude)
        dominant_freq = freqs[dominant_freq_idx]
        
        # Spectral centroid (brightness)
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        
        # Zero crossing rate (roughness indicator)
        zero_crossings = np.sum(np.diff(np.sign(audio)) != 0)
        zero_crossing_rate = zero_crossings / len(audio)
        
        return {
            'rms_level': float(rms),
            'peak_level': float(peak),
            'dynamic_range_db': float(dynamic_range),
            'dominant_frequency': float(dominant_freq),
            'spectral_centroid': float(spectral_centroid),
            'zero_crossing_rate': float(zero_crossing_rate),
            'duration': len(audio) / self.sample_rate,
            'sample_rate': self.sample_rate,
            'clipping_detected': peak >= 0.99
        }
    
    async def normalize_audio(
        self,
        audio: np.ndarray,
        target_level: float = -3.0,  # dB
        method: str = 'peak'
    ) -> np.ndarray:
        """Normalize audio to target level"""
        
        if method == 'peak':
            # Peak normalization
            peak = np.max(np.abs(audio))
            if peak > 0:
                target_linear = 10**(target_level / 20)
                gain = target_linear / peak
                return audio * gain
        
        elif method == 'rms':
            # RMS normalization
            rms = np.sqrt(np.mean(audio**2))
            if rms > 0:
                target_linear = 10**(target_level / 20)
                gain = target_linear / rms
                return audio * gain
        
        return audio
    
    async def remove_silence(
        self,
        audio: np.ndarray,
        threshold: float = -40.0,  # dB
        min_silence_duration: float = 0.1  # seconds
    ) -> np.ndarray:
        """Remove silence from beginning and end of audio"""
        
        threshold_linear = 10**(threshold / 20)
        min_silence_samples = int(min_silence_duration * self.sample_rate)
        
        # Find start of audio
        start_idx = 0
        for i in range(len(audio)):
            if abs(audio[i]) > threshold_linear:
                start_idx = max(0, i - min_silence_samples)
                break
        
        # Find end of audio
        end_idx = len(audio)
        for i in range(len(audio) - 1, -1, -1):
            if abs(audio[i]) > threshold_linear:
                end_idx = min(len(audio), i + min_silence_samples)
                break
        
        return audio[start_idx:end_idx]
