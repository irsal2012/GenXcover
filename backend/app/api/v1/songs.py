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
    try:
        # Create initial song record
        db_song = SongModel(
            title=song_request.title,
            genre=song_request.genre,
            style=song_request.style,
            theme=song_request.theme,
            voice_type=getattr(song_request, 'voice_type', 'Male'),
            creator_id=current_user.id,
            generation_params=song_request.dict()
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        
        # Generate complete song using MusicGenerator
        music_generator = MusicGenerator()
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
        
        # Update song with generated content
        db_song.lyrics = generation_result.get("lyrics", "")
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
        
    except Exception as e:
        logger.error(f"Error generating song: {str(e)}")
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
            detail=f"Failed to generate song: {str(e)}"
        )


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
