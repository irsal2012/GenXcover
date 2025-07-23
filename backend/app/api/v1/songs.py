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
