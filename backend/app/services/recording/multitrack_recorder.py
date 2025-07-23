import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
import uuid
from .audio_processor import AudioProcessor


class MultiTrackRecorder:
    """Multi-track recording service with professional studio features"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bit_depth = 16
        self.audio_processor = AudioProcessor(sample_rate)
        
        # Active recording sessions
        self.recording_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Track templates
        self.track_templates = self._create_track_templates()
        
        # Mixing presets
        self.mixing_presets = self._create_mixing_presets()
    
    def _create_track_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create track templates for different instrument types"""
        return {
            'vocal': {
                'name': 'Vocal Track',
                'color': '#FF6B6B',
                'default_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -18, 'ratio': 3.0}},
                    {'name': 'eq', 'parameters': {'low_gain': -2, 'mid_gain': 2, 'high_gain': 1}},
                    {'name': 'reverb', 'parameters': {'wet_level': 0.2, 'room_size': 0.4}}
                ],
                'suggested_input_gain': 0.7,
                'pan': 0.0,  # Center
                'solo': False,
                'mute': False
            },
            'guitar': {
                'name': 'Guitar Track',
                'color': '#4ECDC4',
                'default_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -16, 'ratio': 2.5}},
                    {'name': 'eq', 'parameters': {'low_gain': 0, 'mid_gain': 1, 'high_gain': 2}},
                    {'name': 'delay', 'parameters': {'delay_time': 0.125, 'feedback': 0.3}}
                ],
                'suggested_input_gain': 0.8,
                'pan': -0.3,  # Slightly left
                'solo': False,
                'mute': False
            },
            'bass': {
                'name': 'Bass Track',
                'color': '#45B7D1',
                'default_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -12, 'ratio': 4.0}},
                    {'name': 'eq', 'parameters': {'low_gain': 3, 'mid_gain': -1, 'high_gain': -2}}
                ],
                'suggested_input_gain': 0.9,
                'pan': 0.0,  # Center
                'solo': False,
                'mute': False
            },
            'drums': {
                'name': 'Drum Track',
                'color': '#F7DC6F',
                'default_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -10, 'ratio': 6.0}},
                    {'name': 'eq', 'parameters': {'low_gain': 2, 'mid_gain': 0, 'high_gain': 3}},
                    {'name': 'reverb', 'parameters': {'wet_level': 0.15, 'room_size': 0.6}}
                ],
                'suggested_input_gain': 0.85,
                'pan': 0.0,  # Center
                'solo': False,
                'mute': False
            },
            'piano': {
                'name': 'Piano Track',
                'color': '#BB8FCE',
                'default_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -20, 'ratio': 2.0}},
                    {'name': 'eq', 'parameters': {'low_gain': 1, 'mid_gain': 0, 'high_gain': 1}},
                    {'name': 'reverb', 'parameters': {'wet_level': 0.25, 'room_size': 0.5}}
                ],
                'suggested_input_gain': 0.75,
                'pan': 0.0,  # Center
                'solo': False,
                'mute': False
            },
            'synth': {
                'name': 'Synthesizer Track',
                'color': '#58D68D',
                'default_effects': [
                    {'name': 'chorus', 'parameters': {'rate': 0.8, 'depth': 0.03}},
                    {'name': 'delay', 'parameters': {'delay_time': 0.25, 'feedback': 0.4}},
                    {'name': 'reverb', 'parameters': {'wet_level': 0.3, 'room_size': 0.7}}
                ],
                'suggested_input_gain': 0.8,
                'pan': 0.2,  # Slightly right
                'solo': False,
                'mute': False
            }
        }
    
    def _create_mixing_presets(self) -> Dict[str, Dict[str, Any]]:
        """Create mixing presets for different genres"""
        return {
            'pop': {
                'name': 'Pop Mix',
                'description': 'Bright, punchy mix suitable for pop music',
                'master_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -6, 'ratio': 2.5}},
                    {'name': 'eq', 'parameters': {'low_gain': 1, 'mid_gain': 0, 'high_gain': 2}}
                ],
                'track_settings': {
                    'vocal': {'volume': 0.85, 'pan': 0.0},
                    'guitar': {'volume': 0.7, 'pan': -0.3},
                    'bass': {'volume': 0.8, 'pan': 0.0},
                    'drums': {'volume': 0.75, 'pan': 0.0}
                }
            },
            'rock': {
                'name': 'Rock Mix',
                'description': 'Powerful, aggressive mix for rock music',
                'master_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -4, 'ratio': 3.0}},
                    {'name': 'eq', 'parameters': {'low_gain': 2, 'mid_gain': 1, 'high_gain': 1}}
                ],
                'track_settings': {
                    'vocal': {'volume': 0.8, 'pan': 0.0},
                    'guitar': {'volume': 0.85, 'pan': -0.4},
                    'bass': {'volume': 0.9, 'pan': 0.0},
                    'drums': {'volume': 0.9, 'pan': 0.0}
                }
            },
            'jazz': {
                'name': 'Jazz Mix',
                'description': 'Warm, natural mix for jazz music',
                'master_effects': [
                    {'name': 'compressor', 'parameters': {'threshold': -12, 'ratio': 1.8}},
                    {'name': 'eq', 'parameters': {'low_gain': 0, 'mid_gain': 1, 'high_gain': -1}}
                ],
                'track_settings': {
                    'vocal': {'volume': 0.75, 'pan': 0.0},
                    'piano': {'volume': 0.8, 'pan': 0.0},
                    'bass': {'volume': 0.7, 'pan': 0.0},
                    'drums': {'volume': 0.65, 'pan': 0.0}
                }
            }
        }
    
    async def create_recording_session(
        self,
        session_name: str,
        user_id: int,
        project_settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new multi-track recording session"""
        
        session_id = str(uuid.uuid4())
        
        default_settings = {
            'sample_rate': self.sample_rate,
            'bit_depth': self.bit_depth,
            'buffer_size': 1024,
            'metronome_enabled': True,
            'metronome_bpm': 120,
            'count_in_bars': 1,
            'auto_punch': False,
            'loop_recording': False
        }
        
        if project_settings:
            default_settings.update(project_settings)
        
        session = {
            'id': session_id,
            'name': session_name,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'settings': default_settings,
            'tracks': {},
            'master_track': {
                'volume': 1.0,
                'effects': [],
                'is_recording': False,
                'is_playing': False
            },
            'timeline': {
                'current_position': 0.0,  # seconds
                'loop_start': 0.0,
                'loop_end': 0.0,
                'markers': []
            },
            'status': 'created'
        }
        
        self.recording_sessions[session_id] = session
        
        return session_id
    
    async def add_track(
        self,
        session_id: str,
        track_type: str = 'vocal',
        track_name: Optional[str] = None
    ) -> str:
        """Add a new track to the recording session"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        track_id = str(uuid.uuid4())
        
        # Get track template
        template = self.track_templates.get(track_type, self.track_templates['vocal'])
        
        track = {
            'id': track_id,
            'name': track_name or f"{template['name']} {len(session['tracks']) + 1}",
            'type': track_type,
            'color': template['color'],
            'volume': 1.0,
            'pan': template['pan'],
            'solo': template['solo'],
            'mute': template['mute'],
            'input_gain': template['suggested_input_gain'],
            'effects': template['default_effects'].copy(),
            'recordings': [],  # List of recorded audio segments
            'is_recording': False,
            'is_armed': False,  # Ready to record
            'monitor': True,    # Monitor input while recording
            'created_at': datetime.now().isoformat()
        }
        
        session['tracks'][track_id] = track
        
        return track_id
    
    async def start_recording(
        self,
        session_id: str,
        track_ids: List[str],
        punch_in: Optional[float] = None,
        punch_out: Optional[float] = None
    ) -> Dict[str, Any]:
        """Start recording on specified tracks"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        
        # Validate track IDs
        for track_id in track_ids:
            if track_id not in session['tracks']:
                raise ValueError(f"Track {track_id} not found in session")
        
        # Set up recording
        recording_info = {
            'session_id': session_id,
            'track_ids': track_ids,
            'start_time': datetime.now().isoformat(),
            'punch_in': punch_in,
            'punch_out': punch_out,
            'status': 'recording'
        }
        
        # Mark tracks as recording
        for track_id in track_ids:
            session['tracks'][track_id]['is_recording'] = True
            session['tracks'][track_id]['is_armed'] = True
        
        session['status'] = 'recording'
        
        return recording_info
    
    async def stop_recording(
        self,
        session_id: str,
        audio_data: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Stop recording and save audio data"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        
        results = {}
        
        for track_id, audio in audio_data.items():
            if track_id in session['tracks']:
                track = session['tracks'][track_id]
                
                # Process audio through track effects
                processed_audio = await self._process_track_audio(audio, track)
                
                # Save recording
                recording_id = str(uuid.uuid4())
                recording_info = {
                    'id': recording_id,
                    'track_id': track_id,
                    'start_position': session['timeline']['current_position'],
                    'duration': len(processed_audio) / self.sample_rate,
                    'audio_data': processed_audio,
                    'recorded_at': datetime.now().isoformat(),
                    'effects_applied': track['effects'].copy()
                }
                
                # Add to track recordings
                track['recordings'].append(recording_info)
                track['is_recording'] = False
                
                # Save audio file
                file_path = await self._save_recording(recording_info, session_id)
                recording_info['file_path'] = file_path
                
                results[track_id] = recording_info
        
        session['status'] = 'stopped'
        
        return results
    
    async def apply_track_effects(
        self,
        session_id: str,
        track_id: str,
        effects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply effects to a track"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        
        if track_id not in session['tracks']:
            raise ValueError(f"Track {track_id} not found")
        
        track = session['tracks'][track_id]
        track['effects'] = effects
        
        # Re-process all recordings on this track
        for recording in track['recordings']:
            if 'audio_data' in recording:
                processed_audio = await self._process_track_audio(
                    recording['audio_data'], track
                )
                recording['processed_audio'] = processed_audio
        
        return {'track_id': track_id, 'effects_applied': effects}
    
    async def mix_tracks(
        self,
        session_id: str,
        mix_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mix all tracks in the session"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        
        # Calculate total duration
        max_duration = 0.0
        for track in session['tracks'].values():
            for recording in track['recordings']:
                end_time = recording['start_position'] + recording['duration']
                max_duration = max(max_duration, end_time)
        
        if max_duration == 0:
            raise ValueError("No recordings found to mix")
        
        # Create mix buffer
        mix_samples = int(max_duration * self.sample_rate)
        mix_buffer = np.zeros(mix_samples)
        
        # Mix each track
        for track_id, track in session['tracks'].items():
            if track['mute']:
                continue
            
            track_buffer = np.zeros(mix_samples)
            
            # Add all recordings from this track
            for recording in track['recordings']:
                start_sample = int(recording['start_position'] * self.sample_rate)
                audio_data = recording.get('processed_audio', recording['audio_data'])
                end_sample = min(start_sample + len(audio_data), mix_samples)
                
                if start_sample < mix_samples:
                    track_buffer[start_sample:end_sample] += audio_data[:end_sample-start_sample]
            
            # Apply track volume and pan
            track_buffer *= track['volume']
            
            # Simple pan implementation (for stereo)
            if track['pan'] != 0:
                # This is a simplified pan - in production you'd use proper stereo panning
                pan_factor = 1.0 - abs(track['pan'])
                track_buffer *= pan_factor
            
            # Add to mix
            mix_buffer += track_buffer
        
        # Apply master effects
        master_track = session['master_track']
        if master_track['effects']:
            mix_buffer = await self.audio_processor.apply_effect_chain(
                mix_buffer, master_track['effects']
            )
        
        # Apply master volume
        mix_buffer *= master_track['volume']
        
        # Normalize to prevent clipping
        mix_buffer = await self.audio_processor.normalize_audio(mix_buffer)
        
        # Save mix
        mix_file_path = await self._save_mix(session_id, mix_buffer)
        
        return {
            'session_id': session_id,
            'mix_file_path': mix_file_path,
            'duration': max_duration,
            'tracks_mixed': len([t for t in session['tracks'].values() if not t['mute']]),
            'sample_rate': self.sample_rate,
            'mixed_at': datetime.now().isoformat()
        }
    
    async def apply_mixing_preset(
        self,
        session_id: str,
        preset_name: str
    ) -> Dict[str, Any]:
        """Apply a mixing preset to the session"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        if preset_name not in self.mixing_presets:
            raise ValueError(f"Mixing preset {preset_name} not found")
        
        session = self.recording_sessions[session_id]
        preset = self.mixing_presets[preset_name]
        
        # Apply master effects
        session['master_track']['effects'] = preset['master_effects']
        
        # Apply track settings
        for track_type, settings in preset['track_settings'].items():
            # Find tracks of this type
            for track in session['tracks'].values():
                if track['type'] == track_type:
                    track['volume'] = settings.get('volume', track['volume'])
                    track['pan'] = settings.get('pan', track['pan'])
        
        return {
            'session_id': session_id,
            'preset_applied': preset_name,
            'preset_description': preset['description']
        }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get detailed information about a recording session"""
        
        if session_id not in self.recording_sessions:
            raise ValueError(f"Recording session {session_id} not found")
        
        session = self.recording_sessions[session_id]
        
        # Calculate session statistics
        total_tracks = len(session['tracks'])
        total_recordings = sum(len(track['recordings']) for track in session['tracks'].values())
        
        total_duration = 0.0
        for track in session['tracks'].values():
            for recording in track['recordings']:
                end_time = recording['start_position'] + recording['duration']
                total_duration = max(total_duration, end_time)
        
        return {
            'session_id': session_id,
            'name': session['name'],
            'user_id': session['user_id'],
            'created_at': session['created_at'],
            'status': session['status'],
            'settings': session['settings'],
            'statistics': {
                'total_tracks': total_tracks,
                'total_recordings': total_recordings,
                'total_duration': total_duration
            },
            'tracks': session['tracks'],
            'master_track': session['master_track'],
            'timeline': session['timeline']
        }
    
    async def _process_track_audio(
        self,
        audio: np.ndarray,
        track: Dict[str, Any]
    ) -> np.ndarray:
        """Process audio through track effects chain"""
        
        processed_audio = audio.copy()
        
        # Apply input gain
        processed_audio *= track['input_gain']
        
        # Apply effects chain
        if track['effects']:
            processed_audio = await self.audio_processor.apply_effect_chain(
                processed_audio, track['effects']
            )
        
        return processed_audio
    
    async def _save_recording(
        self,
        recording_info: Dict[str, Any],
        session_id: str
    ) -> str:
        """Save recording to file"""
        
        # Create recordings directory
        recordings_dir = Path("uploads/recordings") / session_id
        recordings_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"track_{recording_info['track_id']}_{recording_info['id']}.npy"
        file_path = recordings_dir / filename
        
        # Save audio data
        np.save(file_path, recording_info['audio_data'])
        
        # Save metadata
        metadata_path = file_path.with_suffix('.json')
        metadata = {
            'recording_id': recording_info['id'],
            'track_id': recording_info['track_id'],
            'start_position': recording_info['start_position'],
            'duration': recording_info['duration'],
            'recorded_at': recording_info['recorded_at'],
            'sample_rate': self.sample_rate,
            'effects_applied': recording_info['effects_applied']
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    async def _save_mix(self, session_id: str, mix_audio: np.ndarray) -> str:
        """Save final mix to file"""
        
        # Create mixes directory
        mixes_dir = Path("uploads/mixes")
        mixes_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mix_{session_id}_{timestamp}.npy"
        file_path = mixes_dir / filename
        
        # Save mix
        np.save(file_path, mix_audio)
        
        # Save metadata
        metadata_path = file_path.with_suffix('.json')
        metadata = {
            'session_id': session_id,
            'mixed_at': datetime.now().isoformat(),
            'duration': len(mix_audio) / self.sample_rate,
            'sample_rate': self.sample_rate,
            'channels': 1  # Mono for now
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(file_path)
    
    def get_available_effects(self) -> List[str]:
        """Get list of available audio effects"""
        return list(self.audio_processor.effects.keys())
    
    def get_track_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available track templates"""
        return self.track_templates
    
    def get_mixing_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available mixing presets"""
        return self.mixing_presets
