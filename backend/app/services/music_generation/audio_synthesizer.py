import asyncio
import numpy as np
import random
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

class AudioSynthesizer:
    """Audio synthesis service for converting MIDI to audio"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 2  # Stereo
        self.bit_depth = 16
        self.instrument_samples = self._load_instrument_samples()
        self.voice_samples = self._load_voice_samples()
    
    def _load_instrument_samples(self) -> Dict[str, Dict]:
        """Load instrument sample configurations"""
        return {
            'Piano': {
                'waveform': 'sine',
                'attack': 0.1,
                'decay': 0.3,
                'sustain': 0.7,
                'release': 0.5,
                'harmonics': [1.0, 0.5, 0.25, 0.125]
            },
            'Electric Piano': {
                'waveform': 'sine',
                'attack': 0.05,
                'decay': 0.2,
                'sustain': 0.6,
                'release': 0.8,
                'harmonics': [1.0, 0.3, 0.6, 0.2]
            },
            'Electric Bass': {
                'waveform': 'sawtooth',
                'attack': 0.02,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.3,
                'harmonics': [1.0, 0.7, 0.4, 0.2]
            },
            'Drum Kit': {
                'kick': {'frequency': 60, 'decay': 0.5},
                'snare': {'frequency': 200, 'decay': 0.2},
                'hihat': {'frequency': 8000, 'decay': 0.1}
            }
        }
    
    def _load_voice_samples(self) -> Dict[str, Dict]:
        """Load voice synthesis configurations"""
        return {
            'Male': {
                'fundamental_freq_range': (85, 180),  # Hz
                'formants': [730, 1090, 2440],  # Typical male formants
                'vibrato_rate': 6.0,  # Hz
                'vibrato_depth': 0.02
            },
            'Female': {
                'fundamental_freq_range': (165, 265),  # Hz
                'formants': [850, 1220, 2810],  # Typical female formants
                'vibrato_rate': 6.5,  # Hz
                'vibrato_depth': 0.025
            },
            'Child': {
                'fundamental_freq_range': (250, 400),  # Hz
                'formants': [1000, 1400, 3200],  # Typical child formants
                'vibrato_rate': 7.0,  # Hz
                'vibrato_depth': 0.015
            }
        }
    
    async def synthesize_audio(
        self,
        midi_data: Dict[str, Any],
        lyrics: Optional[str] = None,
        voice_type: str = 'Male',
        output_format: str = 'wav'
    ) -> Dict[str, Any]:
        """Synthesize audio from MIDI data and optional lyrics"""
        
        try:
            duration = midi_data.get('duration', 180)
            tempo = midi_data.get('tempo', 120)
            
            # Generate instrumental tracks
            instrumental_audio = await self._synthesize_instrumental(midi_data)
            
            # Add vocals if lyrics provided
            if lyrics:
                vocal_audio = await self._synthesize_vocals(lyrics, midi_data, voice_type)
                # Mix instrumental and vocals
                final_audio = self._mix_audio([instrumental_audio, vocal_audio], [0.7, 0.8])
            else:
                final_audio = instrumental_audio
            
            # Save audio file
            audio_file_path = await self._save_audio_file(final_audio, midi_data['title'], output_format)
            
            return {
                'audio_file_path': audio_file_path,
                'duration': len(final_audio) / self.sample_rate,
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'format': output_format,
                'synthesis_info': {
                    'has_vocals': lyrics is not None,
                    'voice_type': voice_type if lyrics else None,
                    'instrumental_tracks': len(midi_data.get('tracks', {})),
                    'tempo': tempo,
                    'estimated_file_size_mb': len(final_audio) * 2 / (1024 * 1024)  # Rough estimate
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to synthesize audio: {str(e)}")
    
    async def _synthesize_instrumental(self, midi_data: Dict[str, Any]) -> np.ndarray:
        """Synthesize instrumental tracks from MIDI data"""
        
        duration = midi_data.get('duration', 180)
        tracks = midi_data.get('tracks', {})
        
        # Create empty audio buffer
        total_samples = int(duration * self.sample_rate)
        mixed_audio = np.zeros(total_samples, dtype=np.float32)
        
        # Synthesize each track
        for track_name, track_data in tracks.items():
            if track_name == 'drums':
                track_audio = await self._synthesize_drums(track_data, duration)
            else:
                track_audio = await self._synthesize_melodic_track(track_data, track_name, duration)
            
            # Ensure same length
            if len(track_audio) > len(mixed_audio):
                track_audio = track_audio[:len(mixed_audio)]
            elif len(track_audio) < len(mixed_audio):
                padded_audio = np.zeros(len(mixed_audio))
                padded_audio[:len(track_audio)] = track_audio
                track_audio = padded_audio
            
            # Mix with appropriate volume
            volume = self._get_track_volume(track_name)
            mixed_audio += track_audio * volume
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(mixed_audio))
        if max_amplitude > 0:
            mixed_audio = mixed_audio / max_amplitude * 0.8  # Leave some headroom
        
        return mixed_audio
    
    async def _synthesize_melodic_track(self, track_data: List[Dict], track_name: str, duration: float) -> np.ndarray:
        """Synthesize a melodic track (melody, chords, bass)"""
        
        total_samples = int(duration * self.sample_rate)
        track_audio = np.zeros(total_samples, dtype=np.float32)
        
        instrument_config = self.instrument_samples.get(
            self._get_instrument_for_track(track_name), 
            self.instrument_samples['Piano']
        )
        
        for note_info in track_data:
            if isinstance(note_info, dict) and 'note' in note_info:
                # Generate note audio
                note_audio = self._generate_note(
                    note_info['note'],
                    note_info.get('duration', 0.5),
                    note_info.get('velocity', 80),
                    instrument_config
                )
                
                # Place in timeline
                start_sample = int(note_info.get('start_time', 0) * self.sample_rate)
                end_sample = min(start_sample + len(note_audio), total_samples)
                
                if start_sample < total_samples:
                    actual_length = end_sample - start_sample
                    track_audio[start_sample:end_sample] += note_audio[:actual_length]
            
            elif isinstance(note_info, dict) and 'chord' in note_info:
                # Generate chord audio
                chord_audio = self._generate_chord(
                    note_info['chord'],
                    note_info.get('duration', 2.0),
                    note_info.get('velocity', 80),
                    instrument_config
                )
                
                # Place in timeline
                start_sample = int(note_info.get('start_time', 0) * self.sample_rate)
                end_sample = min(start_sample + len(chord_audio), total_samples)
                
                if start_sample < total_samples:
                    actual_length = end_sample - start_sample
                    track_audio[start_sample:end_sample] += chord_audio[:actual_length]
        
        return track_audio
    
    async def _synthesize_drums(self, drum_data: List[Dict], duration: float) -> np.ndarray:
        """Synthesize drum track"""
        
        total_samples = int(duration * self.sample_rate)
        drum_audio = np.zeros(total_samples, dtype=np.float32)
        
        drum_config = self.instrument_samples['Drum Kit']
        
        for hit in drum_data:
            if 'drum' in hit and 'start_time' in hit:
                drum_type = hit['drum']
                start_time = hit['start_time']
                velocity = hit.get('velocity', 100)
                
                # Generate drum hit
                drum_sample = self._generate_drum_hit(drum_type, velocity, drum_config)
                
                # Place in timeline
                start_sample = int(start_time * self.sample_rate)
                end_sample = min(start_sample + len(drum_sample), total_samples)
                
                if start_sample < total_samples:
                    actual_length = end_sample - start_sample
                    drum_audio[start_sample:end_sample] += drum_sample[:actual_length]
        
        return drum_audio
    
    async def _synthesize_vocals(self, lyrics: str, midi_data: Dict, voice_type: str) -> np.ndarray:
        """Synthesize vocal track from lyrics"""
        
        duration = midi_data.get('duration', 180)
        total_samples = int(duration * self.sample_rate)
        
        # Simple vocal synthesis - in reality would use more sophisticated TTS
        vocal_audio = np.zeros(total_samples, dtype=np.float32)
        
        voice_config = self.voice_samples.get(voice_type, self.voice_samples['Male'])
        
        # Split lyrics into words and estimate timing
        words = lyrics.replace('\n', ' ').split()
        words_per_second = 2.5  # Average speaking/singing rate
        
        for i, word in enumerate(words):
            start_time = i / words_per_second
            word_duration = len(word) * 0.1 + 0.2  # Rough estimate
            
            if start_time < duration:
                # Generate vocal sound for word
                word_audio = self._generate_vocal_sound(word, word_duration, voice_config)
                
                start_sample = int(start_time * self.sample_rate)
                end_sample = min(start_sample + len(word_audio), total_samples)
                
                if start_sample < total_samples:
                    actual_length = end_sample - start_sample
                    vocal_audio[start_sample:end_sample] += word_audio[:actual_length]
        
        return vocal_audio
    
    def _generate_note(self, note: str, duration: float, velocity: int, instrument_config: Dict) -> np.ndarray:
        """Generate audio for a single note"""
        
        frequency = self._note_to_frequency(note)
        samples = int(duration * self.sample_rate)
        
        # Generate base waveform
        t = np.linspace(0, duration, samples, False)
        
        if instrument_config['waveform'] == 'sine':
            waveform = np.sin(2 * np.pi * frequency * t)
        elif instrument_config['waveform'] == 'sawtooth':
            waveform = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:  # Default to sine
            waveform = np.sin(2 * np.pi * frequency * t)
        
        # Add harmonics
        for i, harmonic_level in enumerate(instrument_config.get('harmonics', [1.0])):
            if i > 0:  # Skip fundamental (already added)
                harmonic_freq = frequency * (i + 1)
                harmonic_wave = np.sin(2 * np.pi * harmonic_freq * t) * harmonic_level
                waveform += harmonic_wave
        
        # Apply ADSR envelope
        envelope = self._generate_adsr_envelope(samples, instrument_config)
        waveform *= envelope
        
        # Apply velocity
        waveform *= (velocity / 127.0)
        
        return waveform.astype(np.float32)
    
    def _generate_chord(self, chord: str, duration: float, velocity: int, instrument_config: Dict) -> np.ndarray:
        """Generate audio for a chord"""
        
        # Get chord notes (simplified)
        chord_notes = self._chord_to_notes(chord)
        
        # Generate each note and sum them
        chord_audio = None
        for note in chord_notes:
            note_audio = self._generate_note(note, duration, velocity * 0.7, instrument_config)  # Reduce volume per note
            
            if chord_audio is None:
                chord_audio = note_audio
            else:
                chord_audio += note_audio
        
        return chord_audio if chord_audio is not None else np.zeros(int(duration * self.sample_rate))
    
    def _generate_drum_hit(self, drum_type: str, velocity: int, drum_config: Dict) -> np.ndarray:
        """Generate audio for a drum hit"""
        
        if drum_type not in drum_config:
            return np.zeros(int(0.1 * self.sample_rate))  # Silent if unknown drum
        
        config = drum_config[drum_type]
        frequency = config['frequency']
        decay = config['decay']
        
        duration = decay * 2  # Total duration based on decay
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        if drum_type == 'kick':
            # Low frequency sine wave with quick decay
            waveform = np.sin(2 * np.pi * frequency * t)
            envelope = np.exp(-t / decay)
        elif drum_type == 'snare':
            # Mix of sine wave and noise
            waveform = np.sin(2 * np.pi * frequency * t) * 0.5
            noise = np.random.normal(0, 0.3, samples)
            waveform += noise
            envelope = np.exp(-t / decay)
        elif drum_type == 'hihat':
            # High frequency noise
            waveform = np.random.normal(0, 0.2, samples)
            # High-pass filter effect (simplified)
            waveform = np.convolve(waveform, [1, -0.9], mode='same')
            envelope = np.exp(-t / decay)
        else:
            waveform = np.sin(2 * np.pi * frequency * t)
            envelope = np.exp(-t / decay)
        
        waveform *= envelope * (velocity / 127.0)
        
        return waveform.astype(np.float32)
    
    def _generate_vocal_sound(self, word: str, duration: float, voice_config: Dict) -> np.ndarray:
        """Generate vocal sound for a word (simplified)"""
        
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Base frequency (would be more sophisticated in real implementation)
        base_freq = random.uniform(*voice_config['fundamental_freq_range'])
        
        # Generate formant-based vocal sound
        vocal_sound = np.zeros(samples)
        
        for formant_freq in voice_config['formants']:
            formant_wave = np.sin(2 * np.pi * formant_freq * t) * 0.3
            vocal_sound += formant_wave
        
        # Add vibrato
        vibrato_rate = voice_config['vibrato_rate']
        vibrato_depth = voice_config['vibrato_depth']
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        vocal_sound *= vibrato
        
        # Simple envelope
        envelope = np.ones(samples)
        fade_samples = int(0.05 * self.sample_rate)  # 50ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        vocal_sound *= envelope
        
        return vocal_sound.astype(np.float32)
    
    def _generate_adsr_envelope(self, samples: int, instrument_config: Dict) -> np.ndarray:
        """Generate ADSR (Attack, Decay, Sustain, Release) envelope"""
        
        attack = instrument_config.get('attack', 0.1)
        decay = instrument_config.get('decay', 0.3)
        sustain = instrument_config.get('sustain', 0.7)
        release = instrument_config.get('release', 0.5)
        
        envelope = np.ones(samples)
        
        # Attack phase
        attack_samples = int(attack * self.sample_rate)
        if attack_samples > 0 and attack_samples < samples:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        decay_samples = int(decay * self.sample_rate)
        decay_end = min(attack_samples + decay_samples, samples)
        if decay_samples > 0 and attack_samples < samples:
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_end - attack_samples)
        
        # Sustain phase (constant level)
        sustain_end = max(samples - int(release * self.sample_rate), decay_end)
        if sustain_end > decay_end:
            envelope[decay_end:sustain_end] = sustain
        
        # Release phase
        release_samples = samples - sustain_end
        if release_samples > 0:
            envelope[sustain_end:] = np.linspace(sustain, 0, release_samples)
        
        return envelope
    
    def _note_to_frequency(self, note: str) -> float:
        """Convert note name to frequency"""
        
        # Note to semitone mapping
        note_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
                   'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        
        try:
            # Parse note (e.g., "C4", "F#3")
            if len(note) >= 2:
                note_name = note[:-1]
                octave = int(note[-1])
                
                if note_name in note_map:
                    # Calculate frequency using A4 = 440 Hz as reference
                    semitones_from_a4 = (octave - 4) * 12 + note_map[note_name] - 9
                    frequency = 440.0 * (2 ** (semitones_from_a4 / 12.0))
                    return frequency
        except (ValueError, IndexError):
            pass
        
        # Default to middle C if parsing fails
        return 261.63  # C4
    
    def _chord_to_notes(self, chord: str) -> List[str]:
        """Convert chord name to list of notes (simplified)"""
        
        # Remove chord type indicators
        root = chord.replace('maj7', '').replace('m7', '').replace('7', '').replace('m', '')
        
        # Basic chord mappings (simplified)
        chord_patterns = {
            'C': ['C4', 'E4', 'G4'],
            'D': ['D4', 'F#4', 'A4'],
            'E': ['E4', 'G#4', 'B4'],
            'F': ['F4', 'A4', 'C5'],
            'G': ['G4', 'B4', 'D5'],
            'A': ['A4', 'C#5', 'E5'],
            'B': ['B4', 'D#5', 'F#5']
        }
        
        return chord_patterns.get(root, ['C4', 'E4', 'G4'])  # Default to C major
    
    def _get_instrument_for_track(self, track_name: str) -> str:
        """Get instrument name for track"""
        mapping = {
            'melody': 'Piano',
            'chords': 'Electric Piano',
            'bass': 'Electric Bass',
            'drums': 'Drum Kit'
        }
        return mapping.get(track_name, 'Piano')
    
    def _get_track_volume(self, track_name: str) -> float:
        """Get volume level for track"""
        volumes = {
            'melody': 0.8,
            'chords': 0.6,
            'bass': 0.7,
            'drums': 0.9
        }
        return volumes.get(track_name, 0.7)
    
    def _mix_audio(self, audio_tracks: List[np.ndarray], volumes: List[float]) -> np.ndarray:
        """Mix multiple audio tracks"""
        
        if not audio_tracks:
            return np.zeros(0)
        
        # Find maximum length
        max_length = max(len(track) for track in audio_tracks)
        
        # Mix tracks
        mixed = np.zeros(max_length, dtype=np.float32)
        
        for track, volume in zip(audio_tracks, volumes):
            # Pad track if necessary
            if len(track) < max_length:
                padded_track = np.zeros(max_length)
                padded_track[:len(track)] = track
                track = padded_track
            
            mixed += track * volume
        
        # Normalize
        max_amplitude = np.max(np.abs(mixed))
        if max_amplitude > 0:
            mixed = mixed / max_amplitude * 0.8
        
        return mixed
    
    async def _save_audio_file(self, audio_data: np.ndarray, title: str, format: str) -> str:
        """Save audio data to file"""
        
        # Create uploads directory
        uploads_dir = Path("uploads/audio")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{random.randint(1000, 9999)}.npy"  # Save as numpy array for now
        file_path = uploads_dir / filename
        
        # Save audio data (in real implementation, would save as WAV/MP3)
        np.save(file_path, audio_data)
        
        # Also save metadata
        metadata = {
            'title': title,
            'duration': len(audio_data) / self.sample_rate,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'format': format,
            'samples': len(audio_data)
        }
        
        metadata_path = file_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    def analyze_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze audio for various metrics"""
        
        # Basic metrics
        duration = len(audio_data) / self.sample_rate
        rms = np.sqrt(np.mean(audio_data ** 2))
        peak = np.max(np.abs(audio_data))
        
        # Frequency analysis (simplified)
        fft = np.fft.fft(audio_data[:self.sample_rate])  # Analyze first second
        freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
        dominant_freq = abs(freqs[dominant_freq_idx])
        
        return {
            'duration': round(duration, 2),
            'rms_level': round(float(rms), 4),
            'peak_level': round(float(peak), 4),
            'dynamic_range': round(float(peak - rms), 4),
            'dominant_frequency': round(dominant_freq, 2),
            'sample_count': len(audio_data),
            'estimated_loudness': 'quiet' if rms < 0.1 else 'moderate' if rms < 0.3 else 'loud'
        }
