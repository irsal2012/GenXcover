import os
import random
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json

# For MIDI generation, we'll use a simplified approach that can be enhanced later
# with more sophisticated ML models like MusicLM or Magenta

class MIDIGenerator:
    """MIDI generation service for creating instrumental tracks"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.note_mapping = self._create_note_mapping()
        self.chord_progressions = self._load_chord_progressions()
        self.rhythm_patterns = self._load_rhythm_patterns()
    
    def _create_note_mapping(self) -> Dict[str, int]:
        """Create mapping from note names to MIDI numbers"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        mapping = {}
        
        for octave in range(0, 9):
            for i, note in enumerate(notes):
                midi_number = octave * 12 + i
                mapping[f"{note}{octave}"] = midi_number
                
        return mapping
    
    def _load_chord_progressions(self) -> Dict[str, List[List[str]]]:
        """Load common chord progressions by genre"""
        return {
            'Pop': [
                ['C', 'Am', 'F', 'G'],  # vi-IV-I-V
                ['C', 'G', 'Am', 'F'],  # I-V-vi-IV
                ['Am', 'F', 'C', 'G'],  # vi-IV-I-V
            ],
            'Rock': [
                ['E', 'A', 'B', 'E'],   # I-IV-V-I
                ['A', 'D', 'E', 'A'],   # I-IV-V-I in A
                ['G', 'C', 'D', 'G'],   # I-IV-V-I in G
            ],
            'Jazz': [
                ['Cmaj7', 'Am7', 'Dm7', 'G7'],  # ii-V-I
                ['Fmaj7', 'Dm7', 'Gm7', 'C7'], # ii-V-I in F
            ],
            'Blues': [
                ['C7', 'C7', 'C7', 'C7', 'F7', 'F7', 'C7', 'C7', 'G7', 'F7', 'C7', 'G7'],  # 12-bar blues
            ],
            'Electronic': [
                ['Am', 'F', 'C', 'G'],
                ['Dm', 'Bb', 'F', 'C'],
            ]
        }
    
    def _load_rhythm_patterns(self) -> Dict[str, List[float]]:
        """Load rhythm patterns by genre"""
        return {
            'Pop': [1.0, 0.5, 0.75, 0.5, 1.0, 0.5, 0.75, 0.5],  # 4/4 pop rhythm
            'Rock': [1.0, 0.0, 0.75, 0.0, 1.0, 0.0, 0.75, 0.0],  # Rock beat
            'Jazz': [1.0, 0.0, 0.67, 0.33, 1.0, 0.0, 0.67, 0.33],  # Swing rhythm
            'Blues': [1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0],   # Blues shuffle
            'Electronic': [1.0, 0.25, 0.5, 0.25, 1.0, 0.25, 0.5, 0.25],  # Electronic beat
        }
    
    async def generate_midi(
        self,
        title: str,
        genre: str,
        key: str = 'C',
        tempo: int = 120,
        duration: int = 180,  # seconds
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate MIDI track based on parameters"""
        
        try:
            # Generate chord progression
            chord_progression = self._generate_chord_progression(genre, key)
            
            # Generate melody
            melody = self._generate_melody(chord_progression, key, genre)
            
            # Generate bass line
            bass_line = self._generate_bass_line(chord_progression, key)
            
            # Generate drum pattern
            drum_pattern = self._generate_drum_pattern(genre, tempo)
            
            # Create MIDI structure
            midi_data = {
                'title': title,
                'genre': genre,
                'key': key,
                'tempo': tempo,
                'duration': duration,
                'tracks': {
                    'melody': melody,
                    'chords': chord_progression,
                    'bass': bass_line,
                    'drums': drum_pattern
                },
                'metadata': {
                    'time_signature': '4/4',
                    'key_signature': key,
                    'instrument_mapping': {
                        'melody': 'Piano',
                        'chords': 'Electric Piano',
                        'bass': 'Electric Bass',
                        'drums': 'Drum Kit'
                    }
                }
            }
            
            # Save MIDI file (simplified - in real implementation, use python-midi or mido)
            midi_file_path = await self._save_midi_file(midi_data, title)
            
            return {
                'midi_file_path': midi_file_path,
                'midi_data': midi_data,
                'generation_info': {
                    'chord_progression': chord_progression,
                    'key': key,
                    'tempo': tempo,
                    'genre': genre,
                    'estimated_duration': duration
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate MIDI: {str(e)}")
    
    def _generate_chord_progression(self, genre: str, key: str) -> List[Dict[str, Any]]:
        """Generate chord progression for the song"""
        progressions = self.chord_progressions.get(genre, self.chord_progressions['Pop'])
        base_progression = random.choice(progressions)
        
        # Transpose to the correct key if needed
        transposed_progression = self._transpose_progression(base_progression, 'C', key)
        
        # Create chord objects with timing
        chord_progression = []
        for i, chord in enumerate(transposed_progression):
            chord_progression.append({
                'chord': chord,
                'start_time': i * 2.0,  # 2 seconds per chord
                'duration': 2.0,
                'velocity': 80
            })
        
        return chord_progression
    
    def _generate_melody(self, chord_progression: List[Dict], key: str, genre: str) -> List[Dict[str, Any]]:
        """Generate melody line based on chord progression"""
        melody = []
        scale = self._get_scale(key, 'major')  # Simplified to major scale
        
        current_time = 0.0
        note_duration = 0.5  # Half second per note
        
        for chord_info in chord_progression:
            chord_duration = chord_info['duration']
            notes_in_chord = int(chord_duration / note_duration)
            
            for _ in range(notes_in_chord):
                # Choose note from scale (simplified melody generation)
                note = random.choice(scale)
                octave = random.choice([4, 5])  # Middle octaves
                
                melody.append({
                    'note': f"{note}{octave}",
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': random.randint(60, 100)
                })
                
                current_time += note_duration
        
        return melody
    
    def _generate_bass_line(self, chord_progression: List[Dict], key: str) -> List[Dict[str, Any]]:
        """Generate bass line following the chord progression"""
        bass_line = []
        
        for chord_info in chord_progression:
            # Use root note of chord for bass (simplified)
            root_note = chord_info['chord'].replace('maj7', '').replace('m7', '').replace('7', '').replace('m', '')
            
            bass_line.append({
                'note': f"{root_note}2",  # Bass octave
                'start_time': chord_info['start_time'],
                'duration': chord_info['duration'],
                'velocity': 90
            })
        
        return bass_line
    
    def _generate_drum_pattern(self, genre: str, tempo: int) -> List[Dict[str, Any]]:
        """Generate drum pattern based on genre"""
        pattern = self.rhythm_patterns.get(genre, self.rhythm_patterns['Pop'])
        drums = []
        
        beat_duration = 60.0 / tempo  # Duration of one beat
        current_time = 0.0
        
        # Generate 8 bars of drums
        for bar in range(8):
            for i, intensity in enumerate(pattern):
                if intensity > 0:
                    # Kick drum on strong beats
                    if i % 4 == 0:
                        drums.append({
                            'drum': 'kick',
                            'start_time': current_time,
                            'velocity': int(intensity * 127)
                        })
                    
                    # Snare on beats 2 and 4
                    elif i % 4 == 2:
                        drums.append({
                            'drum': 'snare',
                            'start_time': current_time,
                            'velocity': int(intensity * 100)
                        })
                    
                    # Hi-hat on all beats
                    drums.append({
                        'drum': 'hihat',
                        'start_time': current_time,
                        'velocity': int(intensity * 80)
                    })
                
                current_time += beat_duration / 2  # Eighth notes
        
        return drums
    
    def _transpose_progression(self, progression: List[str], from_key: str, to_key: str) -> List[str]:
        """Transpose chord progression to different key"""
        if from_key == to_key:
            return progression
        
        # Simplified transposition (would need more sophisticated logic for real implementation)
        chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        try:
            from_index = chromatic.index(from_key)
            to_index = chromatic.index(to_key)
            interval = (to_index - from_index) % 12
            
            transposed = []
            for chord in progression:
                # Extract root note (simplified)
                root = chord[0]
                if root in chromatic:
                    root_index = chromatic.index(root)
                    new_root_index = (root_index + interval) % 12
                    new_chord = chromatic[new_root_index] + chord[1:]
                    transposed.append(new_chord)
                else:
                    transposed.append(chord)  # Keep as is if can't transpose
            
            return transposed
            
        except (ValueError, IndexError):
            return progression  # Return original if transposition fails
    
    def _get_scale(self, key: str, scale_type: str = 'major') -> List[str]:
        """Get notes in a scale"""
        chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Major scale intervals (whole and half steps)
        major_intervals = [0, 2, 4, 5, 7, 9, 11]
        
        try:
            root_index = chromatic.index(key)
            scale = []
            
            for interval in major_intervals:
                note_index = (root_index + interval) % 12
                scale.append(chromatic[note_index])
            
            return scale
            
        except ValueError:
            # Default to C major if key not found
            return ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    async def _save_midi_file(self, midi_data: Dict[str, Any], title: str) -> str:
        """Save MIDI data to file (simplified JSON format for now)"""
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads/midi")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{random.randint(1000, 9999)}.json"
        file_path = uploads_dir / filename
        
        # Save as JSON (in real implementation, would save as actual MIDI file)
        with open(file_path, 'w') as f:
            json.dump(midi_data, f, indent=2)
        
        return str(file_path)
    
    def analyze_existing_midi(self, midi_file_path: str) -> Dict[str, Any]:
        """Analyze existing MIDI file for features"""
        # This would analyze an actual MIDI file in a real implementation
        return {
            'tempo': 120,
            'key': 'C',
            'time_signature': '4/4',
            'duration': 180,
            'track_count': 4,
            'complexity_score': 0.7
        }
