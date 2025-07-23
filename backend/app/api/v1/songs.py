from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ...core.database import get_db
from ...schemas.song import Song, SongCreate, SongUpdate, SongGenerate, SongList
from ...models.song import Song as SongModel
from ...models.user import User as UserModel
from ...api.deps import get_current_active_user
from ...services.music_generation.music_generator import MusicGenerator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=Song)
def create_song(
    song: SongCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new song"""
    db_song = SongModel(
        **song.dict(),
        creator_id=current_user.id
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


@router.post("/generate", response_model=Song)
async def generate_song(
    song_request: SongGenerate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Generate a complete song with AI"""
    db_song = None
    try:
        # Create initial song record with pending status
        db_song = SongModel(
            title=song_request.title,
            genre=song_request.genre,
            style=song_request.style,
            theme=song_request.theme,
            voice_type=getattr(song_request, 'voice_type', 'Male'),
            creator_id=current_user.id,
            generation_params={
                **song_request.dict(),
                "generation_status": "pending",
                "generation_step": "initializing"
            }
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        
        # Update status to lyrics generation
        db_song.generation_params["generation_step"] = "generating_lyrics"
        db.commit()
        
        # Initialize MusicGenerator and check availability
        music_generator = MusicGenerator()
        
        # Check if MusicGen is available and update status
        if hasattr(music_generator, 'using_musicgen') and music_generator.using_musicgen:
            db_song.generation_params["audio_engine"] = "musicgen"
            db_song.generation_params["audio_quality"] = "high"
        else:
            db_song.generation_params["audio_engine"] = "basic_synthesizer"
            db_song.generation_params["audio_quality"] = "basic"
            logger.warning("MusicGen not available, using basic synthesizer")
        
        db.commit()
        
        # Generate complete song using MusicGenerator
        generation_result = await music_generator.generate_complete_song(
            title=song_request.title,
            genre=song_request.genre,
            theme=song_request.theme,
            style=song_request.style,
            voice_type=getattr(song_request, 'voice_type', 'Male'),
            include_audio=getattr(song_request, 'include_audio', True),
            include_midi=getattr(song_request, 'include_midi', True),
            custom_prompt=getattr(song_request, 'custom_prompt', None)
        )
        
        # Update status to finalizing
        db_song.generation_params["generation_step"] = "finalizing"
        db.commit()
        
        # Update song with generated content
        db_song.lyrics = generation_result.get("lyrics", "")
        db_song.is_generated = True
        
        # Store file paths and convert to URLs
        if generation_result.get("audio_file_path"):
            # Convert local path to URL
            audio_path = generation_result["audio_file_path"]
            db_song.audio_file_path = f"http://localhost:8005/{audio_path}"
        if generation_result.get("midi_file_path"):
            # Convert local path to URL
            midi_path = generation_result["midi_file_path"]
            db_song.midi_file_path = f"http://localhost:8005/{midi_path}"
        
        # Store metadata
        if generation_result.get("duration"):
            db_song.duration = generation_result["duration"]
        if generation_result.get("tempo"):
            db_song.tempo = generation_result["tempo"]
        if generation_result.get("key"):
            db_song.key_signature = generation_result["key"]
        
        # Store audio features and analysis
        if generation_result.get("analysis"):
            db_song.audio_features = generation_result["analysis"]
        
        # Update generation parameters with success status
        db_song.generation_params = {
            **db_song.generation_params,
            "generation_status": "completed",
            "generation_step": "completed",
            "generation_successful": True,
            "generation_timestamp": generation_result.get("generation_timestamp"),
            "files_generated": {
                "audio": generation_result.get("audio_file_path") is not None,
                "midi": generation_result.get("midi_file_path") is not None
            }
        }
        
        db.commit()
        db.refresh(db_song)
        return db_song
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating song: {error_message}")
        
        # Determine user-friendly error message
        user_friendly_error = _get_user_friendly_error(error_message)
        
        # Update song with error status
        if db_song:
            db_song.generation_params = {
                **db_song.generation_params,
                "generation_status": "failed",
                "generation_step": "error",
                "generation_successful": False,
                "error": error_message,
                "user_friendly_error": user_friendly_error
            }
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": user_friendly_error,
                "technical_error": error_message,
                "error_type": _classify_error(error_message),
                "suggestions": _get_error_suggestions(error_message)
            }
        )


def _get_user_friendly_error(error_message: str) -> str:
    """Convert technical error to user-friendly message"""
    error_lower = error_message.lower()
    
    if "musicgen" in error_lower and "not available" in error_lower:
        return "High-quality audio generation is currently unavailable. Using basic audio synthesis instead."
    elif "cuda" in error_lower or "gpu" in error_lower or "memory" in error_lower:
        return "Audio generation failed due to insufficient system resources. Please try again with shorter duration or contact support."
    elif "timeout" in error_lower:
        return "Audio generation is taking longer than expected. Please try again or reduce the song duration."
    elif "azure" in error_lower or "openai" in error_lower:
        return "Lyrics generation service is temporarily unavailable. Please try again later."
    elif "connection" in error_lower or "network" in error_lower:
        return "Network connection issue. Please check your internet connection and try again."
    elif "permission" in error_lower or "access" in error_lower:
        return "Access denied. Please check your account permissions."
    else:
        return "An unexpected error occurred during song generation. Please try again or contact support if the problem persists."


def _classify_error(error_message: str) -> str:
    """Classify error type for better handling"""
    error_lower = error_message.lower()
    
    if "musicgen" in error_lower or "audiocraft" in error_lower:
        return "audio_generation_error"
    elif "cuda" in error_lower or "gpu" in error_lower:
        return "resource_error"
    elif "azure" in error_lower or "openai" in error_lower:
        return "ai_service_error"
    elif "connection" in error_lower or "network" in error_lower:
        return "network_error"
    elif "timeout" in error_lower:
        return "timeout_error"
    else:
        return "unknown_error"


def _get_error_suggestions(error_message: str) -> list:
    """Get suggestions based on error type"""
    error_type = _classify_error(error_message)
    
    suggestions = {
        "audio_generation_error": [
            "Try using basic audio synthesis instead",
            "Check if MusicGen dependencies are installed",
            "Reduce song duration to under 30 seconds"
        ],
        "resource_error": [
            "Try generating shorter songs (under 15 seconds)",
            "Close other applications to free up memory",
            "Contact support for system requirements"
        ],
        "ai_service_error": [
            "Check your internet connection",
            "Verify API credentials are configured",
            "Try again in a few minutes"
        ],
        "network_error": [
            "Check your internet connection",
            "Try again in a few moments",
            "Contact support if problem persists"
        ],
        "timeout_error": [
            "Try generating shorter songs",
            "Reduce complexity by using simpler genres",
            "Try again during off-peak hours"
        ],
        "unknown_error": [
            "Try again in a few minutes",
            "Check your input parameters",
            "Contact support with error details"
        ]
    }
    
    return suggestions.get(error_type, ["Try again later", "Contact support if problem persists"])


@router.post("/generate-lyrics")
async def generate_lyrics_only(
    request: Dict[str, Any]
):
    """Generate only lyrics for a song"""
    try:
        music_generator = MusicGenerator()
        result = await music_generator.generate_lyrics_only(
            title=request.get("title", "Untitled"),
            genre=request.get("genre", "Pop"),
            theme=request.get("theme"),
            style=request.get("style"),
            custom_prompt=request.get("custom_prompt")
        )
        return result
    except Exception as e:
        logger.error(f"Error generating lyrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate lyrics: {str(e)}"
        )


@router.post("/generate-from-lyrics", response_model=Song)
async def generate_song_from_lyrics(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Generate a complete song from existing lyrics"""
    try:
        # Validate required fields
        if not request.get("lyrics"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lyrics are required"
            )
        if not request.get("title"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        
        # Create initial song record
        db_song = SongModel(
            title=request.get("title"),
            genre=request.get("genre", "Pop"),
            style=request.get("style"),
            voice_type=request.get("voice_type", "Male"),
            lyrics=request.get("lyrics"),
            creator_id=current_user.id,
            generation_params={
                **request,
                "generation_type": "from_lyrics"
            }
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        
        # Generate complete song using MusicGenerator
        music_generator = MusicGenerator()
        generation_result = await music_generator.generate_song_from_lyrics(
            lyrics=request.get("lyrics"),
            title=request.get("title"),
            genre=request.get("genre", "Pop"),
            voice_type=request.get("voice_type", "Male"),
            key=request.get("key", "C"),
            tempo=request.get("tempo", 120),
            duration=request.get("duration"),
            include_audio=request.get("include_audio", True),
            include_midi=request.get("include_midi", True),
            style=request.get("style")
        )
        
        # Update song with generated content
        db_song.is_generated = True
        
        # Store file paths
        if generation_result.get("audio_file_path"):
            db_song.audio_file_path = generation_result["audio_file_path"]
        if generation_result.get("midi_file_path"):
            db_song.midi_file_path = generation_result["midi_file_path"]
        
        # Store metadata
        if generation_result.get("duration"):
            db_song.duration = generation_result["duration"]
        if generation_result.get("tempo"):
            db_song.tempo = generation_result["tempo"]
        if generation_result.get("key"):
            db_song.key_signature = generation_result["key"]
        
        # Store audio features and analysis
        if generation_result.get("analysis"):
            db_song.audio_features = generation_result["analysis"]
        
        # Update generation parameters with results
        db_song.generation_params = {
            **db_song.generation_params,
            "generation_successful": True,
            "generation_timestamp": generation_result.get("generation_timestamp"),
            "files_generated": {
                "audio": generation_result.get("audio_file_path") is not None,
                "midi": generation_result.get("midi_file_path") is not None
            }
        }
        
        db.commit()
        db.refresh(db_song)
        return db_song
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating song from lyrics: {str(e)}")
        # Update song with error status
        if 'db_song' in locals():
            db_song.generation_params = {
                **db_song.generation_params,
                "generation_successful": False,
                "error": str(e)
            }
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate song from lyrics: {str(e)}"
        )


@router.get("/", response_model=SongList)
def read_songs(
    skip: int = 0,
    limit: int = 20,
    genre: Optional[str] = None,
    creator_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of public songs"""
    query = db.query(SongModel).filter(SongModel.is_public == True)
    
    if genre:
        query = query.filter(SongModel.genre == genre)
    if creator_id:
        query = query.filter(SongModel.creator_id == creator_id)
    
    total = query.count()
    songs = query.offset(skip).limit(limit).all()
    
    return SongList(
        songs=songs,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/my-songs", response_model=List[Song])
def read_my_songs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user's songs"""
    songs = db.query(SongModel).filter(
        SongModel.creator_id == current_user.id
    ).offset(skip).limit(limit).all()
    return songs


@router.get("/{song_id}", response_model=Song)
def read_song(
    song_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get song by ID"""
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if song is public or user owns it
    if not song.is_public and song.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return song


@router.put("/{song_id}", response_model=Song)
def update_song(
    song_id: int,
    song_update: SongUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update song"""
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if user owns the song
    if song.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update song
    update_data = song_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(song, field, value)
    
    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}")
def delete_song(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete song"""
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if user owns the song
    if song.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(song)
    db.commit()
    return {"message": "Song deleted successfully"}


@router.post("/generate-instrumental")
async def generate_instrumental(
    request: Dict[str, Any]
):
    """Generate instrumental music"""
    try:
        music_generator = MusicGenerator()
        result = await music_generator.generate_instrumental(
            title=request.get("title", "Untitled"),
            genre=request.get("genre", "Pop"),
            key=request.get("key", "C"),
            tempo=request.get("tempo", 120),
            duration=request.get("duration", 180),
            style=request.get("style"),
            include_audio=request.get("include_audio", True)
        )
        return result
    except Exception as e:
        logger.error(f"Error generating instrumental: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate instrumental: {str(e)}"
        )


@router.post("/{song_id}/remix")
async def remix_song(
    song_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Remix an existing song"""
    try:
        # Get the original song
        song = db.query(SongModel).filter(SongModel.id == song_id).first()
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        # Check if song is public or user owns it
        if not song.is_public and song.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        music_generator = MusicGenerator()
        result = await music_generator.remix_song(
            original_song_id=song_id,
            new_genre=request.get("new_genre", "Pop"),
            new_tempo=request.get("new_tempo", 120),
            new_key=request.get("new_key", "C")
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error remixing song: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remix song: {str(e)}"
        )


@router.get("/suggestions/{genre}")
async def get_generation_suggestions(genre: str, theme: Optional[str] = None):
    """Get generation suggestions for a genre"""
    try:
        # Return mock suggestions for now
        return {
            "genre": genre,
            "recommended_tempos": [80, 100, 120, 140, 160],
            "recommended_keys": ["C", "G", "D", "A", "E", "F"],
            "recommended_styles": ["Upbeat", "Melancholic", "Energetic", "Calm", "Dramatic"],
            "recommended_voice_types": ["Male", "Female", "Child", "Choir"],
            "theme_suggestions": ["love", "adventure", "nostalgia", "celebration", "reflection"]
        }
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/metadata/genres")
async def get_supported_genres():
    """Get supported genres"""
    return {
        "genres": ["Pop", "Rock", "Hip Hop", "R&B", "Country", "Electronic", "Jazz", "Classical", "Folk", "Blues", "Reggae", "Punk", "Metal", "Alternative", "Indie"]
    }


@router.get("/metadata/voice-types")
async def get_supported_voice_types():
    """Get supported voice types"""
    return {
        "voice_types": ["Male", "Female", "Child", "Robotic", "Choir", "Instrumental"]
    }


@router.get("/metadata/styles")
async def get_supported_styles():
    """Get supported styles"""
    return {
        "styles": ["Upbeat", "Melancholic", "Energetic", "Calm", "Dramatic", "Romantic", "Aggressive", "Dreamy", "Nostalgic", "Futuristic"]
    }


@router.get("/{song_id}/status")
def get_generation_status(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get generation status for a song"""
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if user owns the song
    if song.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    generation_params = song.generation_params or {}
    
    return {
        "song_id": song_id,
        "status": generation_params.get("generation_status", "unknown"),
        "step": generation_params.get("generation_step", "unknown"),
        "progress": _get_progress_percentage(generation_params.get("generation_step", "unknown")),
        "audio_engine": generation_params.get("audio_engine", "unknown"),
        "audio_quality": generation_params.get("audio_quality", "unknown"),
        "error": generation_params.get("user_friendly_error"),
        "suggestions": generation_params.get("suggestions", []),
        "files_generated": generation_params.get("files_generated", {}),
        "is_completed": generation_params.get("generation_status") == "completed",
        "has_error": generation_params.get("generation_status") == "failed"
    }


def _get_progress_percentage(step: str) -> int:
    """Get progress percentage based on generation step"""
    step_progress = {
        "initializing": 10,
        "generating_lyrics": 30,
        "generating_midi": 50,
        "generating_audio": 80,
        "finalizing": 95,
        "completed": 100,
        "error": 0
    }
    return step_progress.get(step, 0)


@router.post("/check-system-status")
async def check_system_status():
    """Check system status and capabilities"""
    try:
        # Initialize MusicGenerator to check capabilities
        music_generator = MusicGenerator()
        
        # Check MusicGen availability
        musicgen_available = False
        musicgen_info = {}
        
        if hasattr(music_generator, 'musicgen_synthesizer'):
            musicgen_synthesizer = music_generator.musicgen_synthesizer
            if musicgen_synthesizer and musicgen_synthesizer.is_available():
                musicgen_available = True
                musicgen_info = musicgen_synthesizer.get_model_info()
        
        # Check Azure OpenAI availability
        azure_openai_available = False
        try:
            from ...services.azure_openai_client import azure_openai_client
            azure_openai_available = azure_openai_client.is_available()
        except Exception:
            pass
        
        return {
            "system_status": "operational",
            "audio_generation": {
                "musicgen_available": musicgen_available,
                "musicgen_info": musicgen_info,
                "fallback_synthesizer": True,
                "recommended_engine": "musicgen" if musicgen_available else "basic_synthesizer"
            },
            "lyrics_generation": {
                "azure_openai_available": azure_openai_available,
                "fallback_templates": True
            },
            "capabilities": {
                "high_quality_audio": musicgen_available,
                "ai_lyrics": azure_openai_available,
                "midi_generation": True,
                "multiple_genres": True
            },
            "recommendations": _get_system_recommendations(musicgen_available, azure_openai_available)
        }
        
    except Exception as e:
        logger.error(f"Error checking system status: {str(e)}")
        return {
            "system_status": "degraded",
            "error": str(e),
            "audio_generation": {
                "musicgen_available": False,
                "fallback_synthesizer": True,
                "recommended_engine": "basic_synthesizer"
            },
            "lyrics_generation": {
                "azure_openai_available": False,
                "fallback_templates": True
            },
            "capabilities": {
                "high_quality_audio": False,
                "ai_lyrics": False,
                "midi_generation": True,
                "multiple_genres": True
            }
        }


def _get_system_recommendations(musicgen_available: bool, azure_openai_available: bool) -> list:
    """Get system recommendations based on availability"""
    recommendations = []
    
    if not musicgen_available:
        recommendations.append({
            "type": "warning",
            "message": "High-quality audio generation (MusicGen) is not available",
            "action": "Install MusicGen dependencies for better audio quality",
            "priority": "medium"
        })
    
    if not azure_openai_available:
        recommendations.append({
            "type": "info",
            "message": "AI lyrics generation is not configured",
            "action": "Configure Azure OpenAI credentials for AI-powered lyrics",
            "priority": "low"
        })
    
    if musicgen_available and azure_openai_available:
        recommendations.append({
            "type": "success",
            "message": "All AI features are available",
            "action": "You can generate high-quality songs with AI lyrics and audio",
            "priority": "info"
        })
    
    return recommendations
