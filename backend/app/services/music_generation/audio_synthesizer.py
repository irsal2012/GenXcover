import os
import numpy as np
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import asyncio
from datetime import datetime

class AudioSynthesizer:
    """Audio synthesis service for converting MIDI to audio and generating vocals"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.bit_depth = 16
        self.channels = 2  # Stereo
        self.supported_formats = ['wav', 'mp3', 'flac']
        
        # Instrument sound banks (simplified - would use actual samples in production)
        self.instrument_profiles = self._load_instrument_profiles()
        self.vocal_profiles = self._load_vocal_profiles()
    
    def _load_instrument_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load instrument sound profiles"""
        return {
            'Piano': {
                'waveform': 'sine_complex',
                'attack': 0.01,
                'decay': 0.3,
                'sustain': 0.7,
                'release': 1.0,
                'harmonics': [1.0, 0.5, 0.25, 0.125]
            },
            'Electric Piano': {
                'waveform': 'sine_bell',
                'attack': 0.02,
                'decay': 0.5,
                'sustain': 0.6,
                'release': 0.8,
                'harmonics': [1.0, 0.7, 0.3, 0.1]
            },
            'Electric Bass': {
                'waveform': 'sawtooth',
                'attack': 0.01,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.3,
                'harmonics': [1.0, 0.3, 0.1]
            },
            'Acoustic Guitar': {
                'waveform': 'plucked_string',
                'attack': 0.005,
                'decay': 0.2,
                'sustain': 0.4,
                'release': 2.0,
                'harmonics': [1.0, 0.6, 0.4, 0.2, 0.1]
            },
            'Synthesizer': {
                'waveform': 'square',
                'attack': 0.1,
                'decay': 0.2,
                'sustain': 0.7,
                'release': 0.5,
                'harmonics': [1.0, 0.8, 0.6, 0.4]
            }
        }
    
    def _load_vocal_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load vocal synthesis profiles"""
        return {
            'Male': {
                'fundamental_freq_range': (80, 300),
                'formants': [700, 1220, 2600],  # Typical male formants
                'vibrato_rate': 6.0,
                'vibrato_depth': 0.02
            },
            'Female': {
                'fundamental_freq_range': (165, 400),
                'formants': [800, 1400, 2800],  # Typical female formants
                'vibrato_rate': 6.5,
                'vibrato_depth': 0.025
            },
            'Child': {
                'fundamental_freq_range': (200, 500),
                'formants': [900, 1600, 3200],
                'vibrato_rate': 7.0,
                'vibrato_depth': 0.015
            },
            'Robotic': {
                'fundamental_freq_range': (100, 400),
                'formants': [600, 1200, 2400],
                'vibrato_rate': 0.0,  # No vibrato
                'vibrato_depth': 0.0,
                'vocoder_effect': True
            }
        }
    
    async def synthesize_audio(
        self,
        midi_data: Dict[str, Any],
        lyrics: Optional[str] = None,
        voice_type: str = 'Male',
        output_format: str = 'wav'
    ) -> Dict[str, Any]:
        """Synthesize audio from MIDI data and lyrics"""
        
        try:
            # Extract parameters
            title = midi_data.get('title', 'Untitled')
            tempo = midi_data.get('tempo', 120)
            duration = midi_data.get('duration', 180)
            tracks = midi_data.get('tracks', {})
            
            # Generate instrumental tracks
            instrumental_audio = await self._synthesize_instrumental(tracks, tempo, duration)
            
            # Generate vocal track if lyrics provided
            vocal_audio = None
            if lyrics:
                vocal_audio = await self._synthesize_vocals(lyrics, voice_type, tempo, duration)
            
            # Mix all tracks together
            final_audio = await self._mix_tracks(instrumental_audio, vocal_audio)
            
            # Save audio file
            audio_file_path = await self._save_audio_file(final_audio, title, output_format)
            
            return {
                'audio_file_path': audio_file_path,
                'duration': duration,
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'format': output_format,
                'synthesis_info': {
                    'instrumental_tracks': len(tracks),
                    'has_vocals': vocal_audio is not None,
                    'voice_type': voice_type if vocal_audio else None,
                    'tempo': tempo
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to synthesize audio: {str(e)}")
    
    async def _synthesize_instrumental(
        self,
        tracks: Dict[str, List[Dict]],
        tempo: int,
        duration: float
    ) -> Dict[str, np.ndarray]:
        """Synthesize instrumental tracks from MIDI data"""
        
        instrumental_tracks = {}
        
        for track_name, track_data in tracks.items():
            if track_name == 'drums':
                # Handle drums separately
                instrumental_tracks[track_name] = await self._synthesize_drums(track_data, duration)
            else:
                # Handle melodic instruments
                instrumental_tracks[track_name] = await self._synthesize_melodic_track(
                    track_data, track_name, duration
                )
        
        return instrumental_tracks
    
    async def _synthesize_melodic_track(
        self,
        track_data: List[Dict],
        instrument: str,
        duration: float
    ) -> np.ndarray:
        """Synthesize a melodic instrument track"""
        
        # Get instrument profile
        profile = self.instrument_profiles.get(instrument, self.instrument_profiles['Piano'])
        
        # Create audio buffer
        samples = int(duration * self.sample_rate)
        audio = np.zeros(samples)
        
        for note_data in track_data:
            if isinstance(note_data, dict) and 'note' in note_data:
                # Individual note
                note_audio = self._generate_note(
                    note_data['note'],
                    note_data.get('start_time', 0),
                    note_data.get('duration', 1.0),
                    note_data.get('velocity', 80),
                    profile
                )
                
                # Add to track (with bounds checking)
                start_sample = int(note_data.get('start_time', 0) * self.sample_rate)
                end_sample = min(start_sample + len(note_audio), samples)
                
                if start_sample < samples:
                    audio[start_sample:end_sample] += note_audio[:end_sample-start_sample]
            
            elif isinstance(note_data, dict) and 'chord' in note_data:
                # Chord
                chord_audio = self._generate_chord(
                    note_data['chord'],
                    note_data.get('start_time', 0),
                    note_data.get('duration', 2.0),
                    note_data.get('velocity', 80),
                    profile
                )
                
                start_sample = int(note_data.get('start_time', 0) * self.sample_rate)
                end_sample = min(start_sample + len(chord_audio), samples)
                
                if start_sample < samples:
                    audio[start_sample:end_sample] += chord_audio[:end_sample-start_sample]
        
        # Normalize to prevent clipping
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio
    
    async def _synthesize_drums(self, drum_data: List[Dict], duration: float) -> np.ndarray:
        """Synthesize drum track"""
        
        samples = int(duration * self.sample_rate)
        audio = np.zeros(samples)
        
        for hit in drum_data:
            drum_type = hit.get('drum', 'kick')
            start_time = hit.get('start_time', 0)
            velocity = hit.get('velocity', 100)
            
            # Generate drum sound
            drum_audio = self._generate_drum_sound(drum_type, velocity)
            
            # Add to track
            start_sample = int(start_time * self.sample_rate)
            end_sample = min(start_sample + len(drum_audio), samples)
            
            if start_sample < samples:
                audio[start_sample:end_sample] += drum_audio[:end_sample-start_sample]
        
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.9
        
        return audio
    
    async def _synthesize_vocals(
        self,
        lyrics: str,
        voice_type: str,
        tempo: int,
        duration: float
    ) -> np.ndarray:
        """Synthesize vocal track from lyrics (simplified text-to-speech approach)"""
        
        # Get vocal profile
        profile = self.vocal_profiles.get(voice_type, self.vocal_profiles['Male'])
        
        # Create audio buffer
        samples = int(duration * self.sample_rate)
        audio = np.zeros(samples)
        
        # Parse lyrics into phonemes (simplified)
        words = lyrics.split()
        word_duration = duration / len(words) if words else 1.0
        
        # Generate vocal sounds for each word
        for i, word in enumerate(words):
            start_time = i * word_duration
            
            # Generate vocal sound (very simplified - would use proper TTS in production)
            vocal_sound = self._generate_vocal_sound(word, profile, word_duration)
            
            start_sample = int(start_time * self.sample_rate)
            end_sample = min(start_sample + len(vocal_sound), samples)
            
            if start_sample < samples:
                audio[start_sample:end_sample] += vocal_sound[:end_sample-start_sample]
        
        # Apply vocal effects
        audio = self._apply_vocal_effects(audio, profile)
        
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.7
        
        return audio
    
    def _generate_note(
        self,
        note: str,
        start_time: float,
        duration: float,
        velocity: int,
        profile: Dict[str, Any]
    ) -> np.ndarray:
        """Generate audio for a single note"""
        
        # Convert note to frequency
        frequency = self._note_to_frequency(note)
        
        # Generate samples
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Generate waveform based on profile
        waveform_type = profile.get('waveform', 'sine')
        harmonics = profile.get('harmonics', [1.0])
        
        audio = np.zeros(samples)
        
        # Add harmonics
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if waveform_type == 'sine':
                harmonic_wave = np.sin(2 * np.pi * harmonic_freq * t)
            elif waveform_type == 'square':
                harmonic_wave = np.sign(np.sin(2 * np.pi * harmonic_freq * t))
            elif waveform_type == 'sawtooth':
                harmonic_wave = 2 * (t * harmonic_freq - np.floor(t * harmonic_freq + 0.5))
            else:  # Default to sine
                harmonic_wave = np.sin(2 * np.pi * harmonic_freq * t)
            
            audio += harmonic_amp * harmonic_wave
        
        # Apply ADSR envelope
        audio = self._apply_adsr_envelope(audio, profile, velocity)
        
        return audio
    
    def _generate_chord(
        self,
        chord: str,
        start_time: float,
        duration: float,
        velocity: int,
        profile: Dict[str, Any]
    ) -> np.ndarray:
        """Generate audio for a chord"""
        
        # Get chord notes (simplified)
        chord_notes = self._chord_to_notes(chord)
        
        # Generate audio for each note and sum
        chord_audio = None
        
        for note in chord_notes:
            note_audio = self._generate_note(note, 0, duration, velocity, profile)
            
            if chord_audio is None:
                chord_audio = note_audio
            else:
                chord_audio += note_audio
        
        # Normalize chord
        if chord_audio is not None and np.max(np.abs(chord_audio)) > 0:
            chord_audio = chord_audio / np.max(np.abs(chord_audio)) * 0.8
        
        return chord_audio if chord_audio is not None else np.zeros(int(duration * self.sample_rate))
    
    def _generate_drum_sound(self, drum_type: str, velocity: int) -> np.ndarray:
        """Generate drum sound"""
        
        duration = 0.2  # Short drum hit
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        if drum_type == 'kick':
            # Low frequency thump with quick decay
            freq = 60
            audio = np.sin(2 * np.pi * freq * t) * np.exp(-t * 20)
            
        elif drum_type == 'snare':
            # Mix of tone and noise
            freq = 200
            tone = np.sin(2 * np.pi * freq * t) * np.exp(-t * 15)
            noise = np.random.normal(0, 0.1, samples) * np.exp(-t * 25)
            audio = tone + noise
            
        elif drum_type == 'hihat':
            # High frequency noise
            audio = np.random.normal(0, 0.05, samples) * np.exp(-t * 50)
            # High-pass filter effect
            audio = np.diff(np.concatenate([[0], audio]))
            
        else:
            # Default to simple click
            audio = np.random.normal(0, 0.1, samples) * np.exp(-t * 30)
        
        # Apply velocity
        audio = audio * (velocity / 127.0)
        
        return audio
    
    def _generate_vocal_sound(
        self,
        word: str,
        profile: Dict[str, Any],
        duration: float
    ) -> np.ndarray:
        """Generate vocal sound for a word (very simplified)"""
        
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Base frequency (would be determined by melody in real implementation)
        base_freq = random.uniform(*profile['fundamental_freq_range'])
        
        # Generate formant-based vocal sound
        audio = np.zeros(samples)
        
        for formant_freq in profile['formants']:
            # Create formant
            formant = np.sin(2 * np.pi * formant_freq * t)
            # Modulate with base frequency
            carrier = np.sin(2 * np.pi * base_freq * t)
            audio += formant * carrier * 0.3
        
        # Add vibrato if specified
        vibrato_rate = profile.get('vibrato_rate', 0)
        vibrato_depth = profile.get('vibrato_depth', 0)
        
        if vibrato_rate > 0:
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
            audio = audio * vibrato
        
        # Apply envelope
        envelope = np.exp(-t * 2)  # Simple decay
        audio = audio * envelope
        
        return audio
    
    def _apply_vocal_effects(self, audio: np.ndarray, profile: Dict[str, Any]) -> np.ndarray:
        """Apply vocal effects like reverb, compression, etc."""
        
        # Simple reverb effect
        delay_samples = int(0.1 * self.sample_rate)  # 100ms delay
        if len(audio) > delay_samples:
            reverb = np.zeros_like(audio)
            reverb[delay_samples:] = audio[:-delay_samples] * 0.3
            audio = audio + reverb
        
        # Vocoder effect for robotic voice
        if profile.get('vocoder_effect', False):
            # Simple vocoder simulation
            audio = np.sign(audio) * np.abs(audio) ** 0.5
        
        return audio
    
    async def _mix_tracks(
        self,
        instrumental_tracks: Dict[str, np.ndarray],
        vocal_audio: Optional[np.ndarray]
    ) -> np.ndarray:
        """Mix all audio tracks together"""
        
        # Find the longest track to determine final length
        max_length = 0
        for track_audio in instrumental_tracks.values():
            max_length = max(max_length, len(track_audio))
        
        if vocal_audio is not None:
            max_length = max(max_length, len(vocal_audio))
        
        # Create final mix
        final_audio = np.zeros(max_length)
        
        # Mix instrumental tracks
        for track_name, track_audio in instrumental_tracks.items():
            # Pad track to final length
            padded_track = np.zeros(max_length)
            padded_track[:len(track_audio)] = track_audio
            
            # Apply track-specific mixing levels
            if track_name == 'drums':
                final_audio += padded_track * 0.8
            elif track_name == 'bass':
                final_audio += padded_track * 0.7
            else:
                final_audio += padded_track * 0.6
        
        # Add vocals
        if vocal_audio is not None:
            padded_vocals = np.zeros(max_length)
            padded_vocals[:len(vocal_audio)] = vocal_audio
            final_audio += padded_vocals * 0.9  # Vocals prominent
        
        # Master compression and limiting
        final_audio = self._apply_master_effects(final_audio)
        
        return final_audio
    
    def _apply_master_effects(self, audio: np.ndarray) -> np.ndarray:
        """Apply master effects like compression and limiting"""
        
        # Simple compression
        threshold = 0.7
        ratio = 4.0
        
        compressed = np.copy(audio)
        over_threshold = np.abs(compressed) > threshold
        
        compressed[over_threshold] = np.sign(compressed[over_threshold]) * (
            threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio
        )
        
        # Soft limiting
        compressed = np.tanh(compressed * 0.9) * 0.95
        
        return compressed
    
    async def _save_audio_file(
        self,
        audio: np.ndarray,
        title: str,
        output_format: str
    ) -> str:
        """Save audio to file"""
        
        # Create uploads directory
        uploads_dir = Path("uploads/audio")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.{output_format}"
        file_path = uploads_dir / filename
        
        # Convert to 16-bit integers
        audio_int = (audio * 32767).astype(np.int16)
        
        # Save as WAV (simplified - would use proper audio libraries in production)
        # For now, save as numpy array that can be converted later
        np.save(str(file_path).replace(f'.{output_format}', '.npy'), audio_int)
        
        # Also save metadata
        metadata = {
            'sample_rate': self.sample_rate,
            'channels': 1,  # Mono for now
            'duration': len(audio) / self.sample_rate,
            'format': output_format,
            'bit_depth': self.bit_depth
        }
        
        with open(str(file_path).replace(f'.{output_format}', '_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    def _note_to_frequency(self, note: str) -> float:
        """Convert note name to frequency"""
        # Note mapping (A4 = 440 Hz)
        note_frequencies = {
            'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4,
            'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2
        }
        
        try:
            # Parse note (e.g., "C4", "F#5")
            if len(note) >= 2:
                note_name = note[:-1]
                octave = int(note[-1])
                
                # Calculate semitones from A4
                semitones = note_frequencies.get(note_name, 0) + (octave - 4) * 12
                
                # Calculate frequency
                frequency = 440.0 * (2 ** (semitones / 12.0))
                return frequency
            
        except (ValueError, KeyError):
            pass
        
        return 440.0  # Default to A4
    
    def _chord_to_notes(self, chord: str) -> List[str]:
        """Convert chord name to list of notes (simplified)"""
        
        # Basic chord mappings (would be more sophisticated in production)
        chord_patterns = {
            'C': ['C4', 'E4', 'G4'],
            'Dm': ['D4', 'F4', 'A4'],
            'Em': ['E4', 'G4', 'B4'],
            'F': ['F4', 'A4', 'C5'],
            'G': ['G4', 'B4', 'D5'],
            'Am': ['A4', 'C5', 'E5'],
            'Bdim': ['B4', 'D5', 'F5']
        }
        
        # Remove chord extensions for basic lookup
        base_chord = chord.replace('maj7', '').replace('m7', '').replace('7', '')
        
        return chord_patterns.get(base_chord, ['C4', 'E4', 'G4'])
    
    def _apply_adsr_envelope(
        self,
        audio: np.ndarray,
        profile: Dict[str, Any],
        velocity: int
    ) -> np.ndarray:
        """Apply ADSR (Attack, Decay, Sustain, Release) envelope"""
        
        attack_time = profile.get('attack', 0.01)
        decay_time = profile.get('decay', 0.1)
        sustain_level = profile.get('sustain', 0.7)
        release_time = profile.get('release', 0.5)
        
        samples = len(audio)
        envelope = np.ones(samples)
        
        # Attack
        attack_samples = int(attack_time * self.sample_rate)
        if attack_samples > 0 and attack_samples < samples:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_samples = int(decay_time * self.sample_rate)
        decay_end = min(attack_samples + decay_samples, samples)
        if decay_samples > 0 and decay_end > attack_samples:
            envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_end - attack_samples)
        
        # Sustain (constant level)
        sustain_end = max(0, samples - int(release_time * self.sample_rate))
        if sustain_end > decay_end:
            envelope[decay_end:sustain_end] = sustain_level
        
        # Release
        if sustain_end < samples:
            envelope[sustain_end:] = np.linspace(sustain_level, 0, samples - sustain_end)
        
        # Apply velocity
        velocity_factor = velocity / 127.0
        envelope = envelope * velocity_factor
        
        return audio * envelope
