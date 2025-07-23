import asyncio
import os
import random
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import torch
import torchaudio
import numpy as np
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

logger = logging.getLogger(__name__)


class MusicGenSynthesizer:
    """MusicGen-based audio synthesis service for high-quality music generation"""
    
    def __init__(self):
        self.model = None
        self.device = None
        self.sample_rate = 32000  # MusicGen's native sample rate
        self.channels = 1  # MusicGen generates mono audio
        self.model_name = 'musicgen-medium'  # Default model
        self.max_duration = 30  # Maximum generation duration in seconds
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the MusicGen model"""
        try:
            # Check if CUDA is available
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {self.device}")
            
            # Load MusicGen model
            logger.info(f"Loading MusicGen model: {self.model_name}")
            self.model = MusicGen.get_pretrained(self.model_name, device=self.device)
            
            # Set default generation parameters
            self.model.set_generation_params(
                duration=8,  # Default 8 seconds
                temperature=1.0,
                top_k=250,
                top_p=0.0,
                cfg_coef=3.0
            )
            
            logger.info("MusicGen model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MusicGen model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if MusicGen model is available"""
        return self.model is not None
    
    async def synthesize_audio(
        self,
        midi_data: Dict[str, Any],
        lyrics: Optional[str] = None,
        voice_type: str = 'Male',
        output_format: str = 'wav'
    ) -> Dict[str, Any]:
        """Synthesize audio using MusicGen"""
        
        if not self.is_available():
            raise Exception("MusicGen model not available. Please check installation and GPU requirements.")
        
        try:
            # Extract parameters from MIDI data
            title = midi_data.get('title', 'Generated Song')
            genre = midi_data.get('genre', 'pop')
            tempo = midi_data.get('tempo', 120)
            key = midi_data.get('key', 'C')
            duration = min(midi_data.get('duration', 8), self.max_duration)
            
            # Validate duration
            if duration > self.max_duration:
                logger.warning(f"Duration {duration}s exceeds maximum {self.max_duration}s, capping to maximum")
                duration = self.max_duration
            elif duration < 1:
                logger.warning(f"Duration {duration}s too short, setting to 5 seconds")
                duration = 5
            
            # Generate text description for MusicGen
            description = self._create_music_description(
                genre=genre,
                tempo=tempo,
                key=key,
                midi_data=midi_data,
                lyrics=lyrics
            )
            
            logger.info(f"Generating audio with MusicGen: {description} (duration: {duration}s)")
            
            # Set generation duration and check GPU memory
            self.model.set_generation_params(duration=duration)
            
            # Check available GPU memory if using CUDA
            if self.device == 'cuda':
                try:
                    import torch
                    if torch.cuda.is_available():
                        memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
                        memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                        memory_free = memory_total - memory_allocated
                        
                        logger.info(f"GPU Memory: {memory_free:.1f}GB free / {memory_total:.1f}GB total")
                        
                        # Warn if low memory
                        if memory_free < 2.0:  # Less than 2GB free
                            logger.warning(f"Low GPU memory ({memory_free:.1f}GB free). Consider reducing duration or using CPU.")
                except Exception as e:
                    logger.warning(f"Could not check GPU memory: {e}")
            
            # Generate audio with timeout protection
            try:
                wav = await self._generate_audio_async(description)
            except asyncio.TimeoutError:
                raise Exception(f"Audio generation timed out after {duration * 10} seconds. Try reducing duration or complexity.")
            
            # Validate generated audio
            if wav is None or wav.numel() == 0:
                raise Exception("Generated audio is empty. This may indicate a model or memory issue.")
            
            # Process and save audio
            audio_file_path = await self._save_audio_file(wav, title, output_format)
            
            # Calculate metadata
            audio_duration = wav.shape[-1] / self.sample_rate
            
            logger.info(f"Successfully generated {audio_duration:.1f}s of audio using MusicGen")
            
            return {
                'audio_file_path': audio_file_path,
                'duration': audio_duration,
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'format': output_format,
                'synthesis_info': {
                    'model': self.model_name,
                    'description': description,
                    'has_vocals': lyrics is not None,
                    'voice_type': voice_type if lyrics else None,
                    'generation_duration': duration,
                    'device': self.device,
                    'estimated_file_size_mb': wav.numel() * 4 / (1024 * 1024),  # Float32 = 4 bytes
                    'generation_successful': True
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to synthesize audio with MusicGen: {error_msg}")
            
            # Provide more specific error messages
            if "CUDA out of memory" in error_msg or "memory" in error_msg.lower():
                raise Exception("Insufficient GPU memory for audio generation. Try reducing duration to under 15 seconds or use a smaller model.")
            elif "timeout" in error_msg.lower():
                raise Exception("Audio generation timed out. Try reducing duration or complexity.")
            elif "model" in error_msg.lower() and "not" in error_msg.lower():
                raise Exception("MusicGen model failed to load. Check installation and system requirements.")
            else:
                raise Exception(f"MusicGen audio synthesis failed: {error_msg}")
    
    async def _generate_audio_async(self, description: str) -> torch.Tensor:
        """Generate audio asynchronously to avoid blocking"""
        
        def _generate():
            with torch.no_grad():
                wav = self.model.generate([description])
                return wav[0].cpu()  # Return first (and only) generated sample
        
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        wav = await loop.run_in_executor(None, _generate)
        
        return wav
    
    def _create_music_description(
        self,
        genre: str,
        tempo: int,
        key: str,
        midi_data: Dict[str, Any],
        lyrics: Optional[str] = None
    ) -> str:
        """Create a text description for MusicGen based on musical parameters"""
        
        # Base description with genre
        description_parts = []
        
        # Add genre
        genre_lower = genre.lower()
        if genre_lower in ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hip hop', 'country', 'blues']:
            description_parts.append(f"{genre_lower} music")
        else:
            description_parts.append("pop music")  # Default fallback
        
        # Add tempo description
        if tempo < 80:
            description_parts.append("slow tempo")
        elif tempo < 120:
            description_parts.append("medium tempo")
        elif tempo < 140:
            description_parts.append("upbeat")
        else:
            description_parts.append("fast tempo")
        
        # Add key information (simplified)
        if key.endswith('m') or 'minor' in key.lower():
            description_parts.append("minor key")
        else:
            description_parts.append("major key")
        
        # Add instrumentation based on MIDI tracks
        tracks = midi_data.get('tracks', {})
        instruments = []
        
        if 'melody' in tracks:
            instruments.append("piano")
        if 'chords' in tracks:
            instruments.append("guitar")
        if 'bass' in tracks:
            instruments.append("bass")
        if 'drums' in tracks:
            instruments.append("drums")
        
        if instruments:
            if len(instruments) == 1:
                description_parts.append(f"with {instruments[0]}")
            elif len(instruments) == 2:
                description_parts.append(f"with {instruments[0]} and {instruments[1]}")
            else:
                description_parts.append(f"with {', '.join(instruments[:-1])}, and {instruments[-1]}")
        
        # Add mood/style based on genre
        mood_map = {
            'pop': ['catchy', 'uplifting', 'energetic'],
            'rock': ['powerful', 'driving', 'energetic'],
            'jazz': ['smooth', 'sophisticated', 'relaxed'],
            'classical': ['elegant', 'orchestral', 'refined'],
            'electronic': ['synthetic', 'modern', 'rhythmic'],
            'hip hop': ['rhythmic', 'urban', 'strong beat'],
            'country': ['acoustic', 'storytelling', 'warm'],
            'blues': ['soulful', 'emotional', 'expressive']
        }
        
        if genre_lower in mood_map:
            mood = random.choice(mood_map[genre_lower])
            description_parts.append(mood)
        
        # Add vocal information if lyrics provided
        if lyrics:
            description_parts.append("with vocals")
            # Try to detect song structure from lyrics
            if 'chorus' in lyrics.lower() or 'verse' in lyrics.lower():
                description_parts.append("verse-chorus structure")
        else:
            description_parts.append("instrumental")
        
        # Combine all parts
        description = ", ".join(description_parts)
        
        # Ensure description is not too long (MusicGen has token limits)
        if len(description) > 200:
            description = description[:200].rsplit(',', 1)[0]  # Cut at last comma
        
        return description
    
    async def generate_instrumental(
        self,
        title: str,
        genre: str,
        key: str = 'C',
        tempo: int = 120,
        duration: int = 8,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate instrumental track using MusicGen"""
        
        if not self.is_available():
            raise Exception("MusicGen model not available")
        
        try:
            # Create description for instrumental
            description_parts = [f"{genre.lower()} instrumental"]
            
            # Add tempo
            if tempo < 80:
                description_parts.append("slow")
            elif tempo < 120:
                description_parts.append("medium tempo")
            else:
                description_parts.append("upbeat")
            
            # Add style if provided
            if style:
                description_parts.append(style.lower())
            
            # Add key mood
            if key.endswith('m') or 'minor' in key.lower():
                description_parts.append("minor key")
            else:
                description_parts.append("major key")
            
            description = ", ".join(description_parts)
            
            # Set duration
            duration = min(duration, self.max_duration)
            self.model.set_generation_params(duration=duration)
            
            # Generate audio
            wav = await self._generate_audio_async(description)
            
            # Save audio
            audio_file_path = await self._save_audio_file(wav, title, 'wav')
            
            return {
                'title': title,
                'genre': genre,
                'key': key,
                'tempo': tempo,
                'duration': wav.shape[-1] / self.sample_rate,
                'audio_file_path': audio_file_path,
                'description': description,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Failed to generate instrumental: {e}")
            raise Exception(f"Failed to generate instrumental: {str(e)}")
    
    async def generate_from_prompt(
        self,
        prompt: str,
        duration: int = 8,
        title: str = "Generated Music"
    ) -> Dict[str, Any]:
        """Generate music directly from a text prompt"""
        
        if not self.is_available():
            raise Exception("MusicGen model not available")
        
        try:
            # Set duration
            duration = min(duration, self.max_duration)
            self.model.set_generation_params(duration=duration)
            
            # Generate audio
            wav = await self._generate_audio_async(prompt)
            
            # Save audio
            audio_file_path = await self._save_audio_file(wav, title, 'wav')
            
            return {
                'title': title,
                'prompt': prompt,
                'duration': wav.shape[-1] / self.sample_rate,
                'audio_file_path': audio_file_path,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Failed to generate from prompt: {e}")
            raise Exception(f"Failed to generate from prompt: {str(e)}")
    
    async def _save_audio_file(self, wav: torch.Tensor, title: str, format: str) -> str:
        """Save audio tensor to file"""
        
        try:
            # Create uploads directory
            uploads_dir = Path("uploads/audio")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{random.randint(1000, 9999)}"
            file_path = uploads_dir / filename
            
            # Save audio using audiocraft's audio_write function
            # This handles format conversion and normalization
            audio_write(
                str(file_path),
                wav,
                self.sample_rate,
                strategy="loudness",  # Normalize loudness
                loudness_headroom_db=14,
                loudness_compressor=True,
                add_suffix=True  # Automatically adds .wav extension
            )
            
            # Find the actual saved file (audio_write adds extension)
            saved_files = list(uploads_dir.glob(f"{filename}.*"))
            if saved_files:
                actual_file_path = str(saved_files[0])
            else:
                actual_file_path = str(file_path) + ".wav"
            
            # Save metadata
            metadata = {
                'title': title,
                'duration': float(wav.shape[-1] / self.sample_rate),
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'format': format,
                'model': self.model_name,
                'samples': int(wav.shape[-1])
            }
            
            metadata_path = Path(actual_file_path).with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return actual_file_path
            
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            raise Exception(f"Failed to save audio file: {str(e)}")
    
    def analyze_audio(self, wav: torch.Tensor) -> Dict[str, Any]:
        """Analyze generated audio for various metrics"""
        
        try:
            # Convert to numpy for analysis
            audio_np = wav.numpy().flatten()
            
            # Basic metrics
            duration = len(audio_np) / self.sample_rate
            rms = np.sqrt(np.mean(audio_np ** 2))
            peak = np.max(np.abs(audio_np))
            
            # Dynamic range
            dynamic_range = peak - rms if peak > 0 else 0
            
            # Frequency analysis (simplified)
            if len(audio_np) > self.sample_rate:
                fft = np.fft.fft(audio_np[:self.sample_rate])  # Analyze first second
                freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
                magnitude = np.abs(fft)
                
                # Find dominant frequency
                dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
                dominant_freq = abs(freqs[dominant_freq_idx])
            else:
                dominant_freq = 0
            
            return {
                'duration': round(duration, 2),
                'rms_level': round(float(rms), 4),
                'peak_level': round(float(peak), 4),
                'dynamic_range': round(float(dynamic_range), 4),
                'dominant_frequency': round(dominant_freq, 2),
                'sample_count': len(audio_np),
                'estimated_loudness': 'quiet' if rms < 0.1 else 'moderate' if rms < 0.3 else 'loud',
                'quality_score': min(1.0, dynamic_range * 2)  # Simple quality metric
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze audio: {e}")
            return {
                'duration': 0,
                'rms_level': 0,
                'peak_level': 0,
                'dynamic_range': 0,
                'dominant_frequency': 0,
                'sample_count': 0,
                'estimated_loudness': 'unknown',
                'quality_score': 0,
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        
        if not self.is_available():
            return {
                'available': False,
                'error': 'Model not loaded'
            }
        
        return {
            'available': True,
            'model_name': self.model_name,
            'device': self.device,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'max_duration': self.max_duration,
            'cuda_available': torch.cuda.is_available(),
            'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None
        }
    
    def set_generation_params(
        self,
        duration: int = 8,
        temperature: float = 1.0,
        top_k: int = 250,
        top_p: float = 0.0,
        cfg_coef: float = 3.0
    ):
        """Set generation parameters for MusicGen"""
        
        if self.is_available():
            duration = min(duration, self.max_duration)
            self.model.set_generation_params(
                duration=duration,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                cfg_coef=cfg_coef
            )
