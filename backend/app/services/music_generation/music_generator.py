import asyncio
from typing import Dict, Any, Optional
from .lyrics_generator import LyricsGenerator
from .midi_generator import MIDIGenerator
from .audio_synthesizer import AudioSynthesizer


class MusicGenerator:
    """Comprehensive music generation service that orchestrates all components"""
    
    def __init__(self):
        self.lyrics_generator = LyricsGenerator()
        self.midi_generator = MIDIGenerator()
        self.audio_synthesizer = AudioSynthesizer()
    
    async def generate_complete_song(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        voice_type: str = 'Male',
        key: str = 'C',
        tempo: int = 120,
        duration: int = 180,
        include_audio: bool = True,
        include_midi: bool = True,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete song with lyrics, MIDI, and audio"""
        
        try:
            generation_results = {
                'title': title,
                'genre': genre,
                'theme': theme,
                'style': style,
                'voice_type': voice_type,
                'key': key,
                'tempo': tempo,
                'duration': duration,
                'generation_timestamp': asyncio.get_event_loop().time()
            }
            
            # Step 1: Generate lyrics
            print(f"🎵 Generating lyrics for '{title}'...")
            lyrics_result = await self.lyrics_generator.generate_lyrics(
                title=title,
                genre=genre,
                theme=theme,
                style=style,
                custom_prompt=custom_prompt
            )
            
            generation_results['lyrics'] = lyrics_result['lyrics']
            generation_results['lyrics_structure'] = lyrics_result['structure']
            generation_results['lyrics_metadata'] = lyrics_result['metadata']
            
            # Update duration based on lyrics if available
            if 'estimated_duration' in lyrics_result['metadata']:
                duration = max(duration, lyrics_result['metadata']['estimated_duration'])
                generation_results['duration'] = duration
            
            # Step 2: Generate MIDI if requested
            midi_result = None
            if include_midi:
                print(f"🎹 Generating MIDI arrangement...")
                midi_result = await self.midi_generator.generate_midi(
                    title=title,
                    genre=genre,
                    key=key,
                    tempo=tempo,
                    duration=duration,
                    style=style
                )
                
                generation_results['midi_file_path'] = midi_result['midi_file_path']
                generation_results['midi_data'] = midi_result['midi_data']
                generation_results['chord_progression'] = midi_result['generation_info']['chord_progression']
            
            # Step 3: Generate audio if requested
            audio_result = None
            if include_audio and midi_result:
                print(f"🔊 Synthesizing audio...")
                audio_result = await self.audio_synthesizer.synthesize_audio(
                    midi_data=midi_result['midi_data'],
                    lyrics=lyrics_result['lyrics'],
                    voice_type=voice_type,
                    output_format='wav'
                )
                
                generation_results['audio_file_path'] = audio_result['audio_file_path']
                generation_results['audio_metadata'] = {
                    'duration': audio_result['duration'],
                    'sample_rate': audio_result['sample_rate'],
                    'channels': audio_result['channels'],
                    'format': audio_result['format']
                }
                generation_results['synthesis_info'] = audio_result['synthesis_info']
            
            # Step 4: Analyze generated content
            analysis = await self._analyze_generated_song(generation_results)
            generation_results['analysis'] = analysis
            
            print(f"✅ Song generation complete!")
            return generation_results
            
        except Exception as e:
            raise Exception(f"Failed to generate complete song: {str(e)}")
    
    async def generate_lyrics_only(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate only lyrics for a song"""
        
        return await self.lyrics_generator.generate_lyrics(
            title=title,
            genre=genre,
            theme=theme,
            style=style,
            custom_prompt=custom_prompt
        )
    
    async def generate_instrumental(
        self,
        title: str,
        genre: str,
        key: str = 'C',
        tempo: int = 120,
        duration: int = 180,
        style: Optional[str] = None,
        include_audio: bool = True
    ) -> Dict[str, Any]:
        """Generate instrumental track (MIDI + audio)"""
        
        try:
            # Generate MIDI
            midi_result = await self.midi_generator.generate_midi(
                title=title,
                genre=genre,
                key=key,
                tempo=tempo,
                duration=duration,
                style=style
            )
            
            result = {
                'title': title,
                'genre': genre,
                'key': key,
                'tempo': tempo,
                'duration': duration,
                'midi_file_path': midi_result['midi_file_path'],
                'midi_data': midi_result['midi_data'],
                'chord_progression': midi_result['generation_info']['chord_progression']
            }
            
            # Generate audio if requested
            if include_audio:
                audio_result = await self.audio_synthesizer.synthesize_audio(
                    midi_data=midi_result['midi_data'],
                    lyrics=None,  # No vocals for instrumental
                    voice_type='Male',  # Not used
                    output_format='wav'
                )
                
                result['audio_file_path'] = audio_result['audio_file_path']
                result['audio_metadata'] = {
                    'duration': audio_result['duration'],
                    'sample_rate': audio_result['sample_rate'],
                    'channels': audio_result['channels'],
                    'format': audio_result['format']
                }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate instrumental: {str(e)}")
    
    async def add_vocals_to_instrumental(
        self,
        midi_data: Dict[str, Any],
        lyrics: str,
        voice_type: str = 'Male'
    ) -> Dict[str, Any]:
        """Add vocals to existing instrumental track"""
        
        try:
            audio_result = await self.audio_synthesizer.synthesize_audio(
                midi_data=midi_data,
                lyrics=lyrics,
                voice_type=voice_type,
                output_format='wav'
            )
            
            return {
                'audio_file_path': audio_result['audio_file_path'],
                'audio_metadata': {
                    'duration': audio_result['duration'],
                    'sample_rate': audio_result['sample_rate'],
                    'channels': audio_result['channels'],
                    'format': audio_result['format']
                },
                'synthesis_info': audio_result['synthesis_info']
            }
            
        except Exception as e:
            raise Exception(f"Failed to add vocals: {str(e)}")
    
    async def remix_song(
        self,
        original_midi_data: Dict[str, Any],
        new_genre: str,
        new_tempo: Optional[int] = None,
        new_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remix an existing song with different genre/tempo/key"""
        
        try:
            # Extract original parameters
            title = original_midi_data.get('title', 'Remixed Song')
            original_tempo = original_midi_data.get('tempo', 120)
            original_key = original_midi_data.get('key', 'C')
            duration = original_midi_data.get('duration', 180)
            
            # Use new parameters or keep originals
            remix_tempo = new_tempo if new_tempo else original_tempo
            remix_key = new_key if new_key else original_key
            
            # Generate new MIDI with different style
            remix_midi = await self.midi_generator.generate_midi(
                title=f"{title} ({new_genre} Remix)",
                genre=new_genre,
                key=remix_key,
                tempo=remix_tempo,
                duration=duration
            )
            
            # Generate new audio
            remix_audio = await self.audio_synthesizer.synthesize_audio(
                midi_data=remix_midi['midi_data'],
                lyrics=None,  # Keep instrumental for remix
                voice_type='Male',
                output_format='wav'
            )
            
            return {
                'title': f"{title} ({new_genre} Remix)",
                'original_genre': original_midi_data.get('genre', 'Unknown'),
                'new_genre': new_genre,
                'tempo_change': f"{original_tempo} → {remix_tempo}",
                'key_change': f"{original_key} → {remix_key}",
                'midi_file_path': remix_midi['midi_file_path'],
                'audio_file_path': remix_audio['audio_file_path'],
                'remix_info': {
                    'original_tempo': original_tempo,
                    'new_tempo': remix_tempo,
                    'original_key': original_key,
                    'new_key': remix_key,
                    'genre_change': f"{original_midi_data.get('genre', 'Unknown')} → {new_genre}"
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to remix song: {str(e)}")
    
    async def _analyze_generated_song(self, generation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the generated song for quality and characteristics"""
        
        analysis = {
            'generation_quality': 'good',  # Would use ML models in production
            'estimated_appeal': 0.75,  # 0-1 scale
            'complexity_score': 0.6,
            'genre_consistency': 0.8,
            'lyrical_coherence': 0.85,
            'musical_structure': 'verse-chorus-verse-chorus-bridge-chorus',
            'recommendations': []
        }
        
        # Analyze lyrics if available
        if 'lyrics' in generation_results:
            lyrics = generation_results['lyrics']
            word_count = len(lyrics.split())
            
            analysis['lyrics_analysis'] = {
                'word_count': word_count,
                'estimated_singability': 0.8,
                'emotional_tone': 'positive',  # Would use sentiment analysis
                'complexity': 'medium'
            }
            
            if word_count < 50:
                analysis['recommendations'].append("Consider adding more verses for a fuller song")
            elif word_count > 200:
                analysis['recommendations'].append("Song might be too long, consider shortening")
        
        # Analyze musical elements
        if 'chord_progression' in generation_results:
            chord_count = len(generation_results['chord_progression'])
            analysis['musical_analysis'] = {
                'chord_progression_length': chord_count,
                'harmonic_complexity': 'medium',
                'key_stability': 'stable'
            }
            
            if chord_count < 4:
                analysis['recommendations'].append("Consider adding more chord variety")
        
        # Analyze audio if available
        if 'audio_metadata' in generation_results:
            duration = generation_results['audio_metadata']['duration']
            analysis['audio_analysis'] = {
                'duration': duration,
                'dynamic_range': 'good',
                'frequency_balance': 'balanced'
            }
            
            if duration < 120:
                analysis['recommendations'].append("Song is quite short, consider extending")
            elif duration > 300:
                analysis['recommendations'].append("Song is quite long, might lose listener attention")
        
        # Genre-specific analysis
        genre = generation_results.get('genre', 'Unknown')
        if genre in ['Pop', 'Rock']:
            if generation_results.get('tempo', 120) < 100:
                analysis['recommendations'].append(f"Tempo might be slow for {genre}, consider increasing")
        elif genre == 'Ballad':
            if generation_results.get('tempo', 120) > 100:
                analysis['recommendations'].append("Tempo might be fast for a ballad, consider slowing down")
        
        return analysis
    
    async def get_generation_suggestions(
        self,
        genre: str,
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get suggestions for song generation parameters"""
        
        suggestions = {
            'genre': genre,
            'recommended_tempos': [],
            'recommended_keys': [],
            'recommended_styles': [],
            'recommended_voice_types': [],
            'theme_suggestions': []
        }
        
        # Genre-specific suggestions
        if genre.lower() == 'pop':
            suggestions.update({
                'recommended_tempos': [120, 128, 132],
                'recommended_keys': ['C', 'G', 'D', 'A'],
                'recommended_styles': ['Upbeat', 'Energetic', 'Catchy'],
                'recommended_voice_types': ['Male', 'Female'],
                'theme_suggestions': ['Love', 'Freedom', 'Dreams', 'Youth']
            })
        elif genre.lower() == 'rock':
            suggestions.update({
                'recommended_tempos': [120, 140, 160],
                'recommended_keys': ['E', 'A', 'D', 'G'],
                'recommended_styles': ['Energetic', 'Aggressive', 'Powerful'],
                'recommended_voice_types': ['Male', 'Female'],
                'theme_suggestions': ['Rebellion', 'Freedom', 'Power', 'Struggle']
            })
        elif genre.lower() == 'jazz':
            suggestions.update({
                'recommended_tempos': [100, 120, 140],
                'recommended_keys': ['Bb', 'F', 'C', 'G'],
                'recommended_styles': ['Smooth', 'Sophisticated', 'Improvisational'],
                'recommended_voice_types': ['Male', 'Female'],
                'theme_suggestions': ['Love', 'Night', 'City', 'Romance']
            })
        elif genre.lower() == 'electronic':
            suggestions.update({
                'recommended_tempos': [128, 130, 140],
                'recommended_keys': ['Am', 'Em', 'Dm', 'Gm'],
                'recommended_styles': ['Futuristic', 'Energetic', 'Atmospheric'],
                'recommended_voice_types': ['Male', 'Female', 'Robotic'],
                'theme_suggestions': ['Future', 'Technology', 'Space', 'Energy']
            })
        else:
            # Default suggestions
            suggestions.update({
                'recommended_tempos': [120, 130, 140],
                'recommended_keys': ['C', 'G', 'D', 'A'],
                'recommended_styles': ['Upbeat', 'Melodic', 'Emotional'],
                'recommended_voice_types': ['Male', 'Female'],
                'theme_suggestions': ['Love', 'Life', 'Dreams', 'Hope']
            })
        
        return suggestions
    
    def get_supported_genres(self) -> list:
        """Get list of supported genres"""
        return ['Pop', 'Rock', 'Hip Hop', 'R&B', 'Country', 'Electronic', 
                'Jazz', 'Classical', 'Folk', 'Blues', 'Reggae', 'Punk', 
                'Metal', 'Alternative', 'Indie']
    
    def get_supported_voice_types(self) -> list:
        """Get list of supported voice types"""
        return ['Male', 'Female', 'Child', 'Robotic', 'Choir']
    
    def get_supported_styles(self) -> list:
        """Get list of supported styles"""
        return ['Upbeat', 'Melancholic', 'Energetic', 'Calm', 'Dramatic', 
                'Romantic', 'Aggressive', 'Dreamy', 'Nostalgic', 'Futuristic']
