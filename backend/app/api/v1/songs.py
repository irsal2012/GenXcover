from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...schemas.song import Song, SongCreate, SongUpdate, SongGenerate, SongList
from ...models.song import Song as SongModel
from ...models.user import User as UserModel
from ...api.deps import get_current_active_user
from ...services.music_generation.music_generator import MusicGenerator

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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a new song with AI"""
    # Create initial song record (using dummy user ID for testing)
    db_song = SongModel(
        title=song_request.title,
        genre=song_request.genre,
        style=song_request.style,
        theme=song_request.theme,
        voice_type=song_request.voice_type,
        creator_id=1,  # Dummy user ID for testing
        generation_params=song_request.dict()
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    
    # Generate complete song using MusicGenerator
    try:
        music_generator = MusicGenerator()
        generation_result = await music_generator.generate_complete_song(
            title=song_request.title,
            genre=song_request.genre,
            theme=song_request.theme,
            style=song_request.style,
            voice_type=song_request.voice_type,
            include_audio=song_request.include_audio,
            include_midi=song_request.include_midi,
            custom_prompt=song_request.custom_prompt
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
        
    except Exception as e:
        # Update song with error status
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
    
    return db_song


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
def read_song(song_id: int, db: Session = Depends(get_db)):
    """Get song by ID"""
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if song is public or user owns it
    # For now, we'll allow access to all songs
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


@router.post("/generate-lyrics")
async def generate_lyrics_only(
    request: dict,
    current_user: UserModel = Depends(get_current_active_user)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate lyrics: {str(e)}"
        )


@router.post("/generate-instrumental")
async def generate_instrumental(
    request: dict,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Generate instrumental track (MIDI + audio)"""
    try:
        music_generator = MusicGenerator()
        result = await music_generator.generate_instrumental(
            title=request.get("title", "Untitled Instrumental"),
            genre=request.get("genre", "Pop"),
            key=request.get("key", "C"),
            tempo=request.get("tempo", 120),
            duration=request.get("duration", 180),
            style=request.get("style"),
            include_audio=request.get("include_audio", True)
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate instrumental: {str(e)}"
        )


@router.post("/{song_id}/remix")
async def remix_song(
    song_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Remix an existing song with different genre/tempo/key"""
    # Get original song
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    # Check if user owns the song or it's public
    if song.creator_id != current_user.id and not song.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        music_generator = MusicGenerator()
        
        # Create original MIDI data from song
        original_midi_data = {
            "title": song.title,
            "genre": song.genre,
            "key": song.key_signature or "C",
            "tempo": song.tempo or 120,
            "duration": song.duration or 180
        }
        
        result = await music_generator.remix_song(
            original_midi_data=original_midi_data,
            new_genre=request.get("new_genre", song.genre),
            new_tempo=request.get("new_tempo"),
            new_key=request.get("new_key")
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remix song: {str(e)}"
        )


@router.get("/suggestions/{genre}")
async def get_generation_suggestions(
    genre: str,
    theme: Optional[str] = None
):
    """Get suggestions for song generation parameters"""
    try:
        music_generator = MusicGenerator()
        suggestions = await music_generator.get_generation_suggestions(genre, theme)
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/metadata/genres")
def get_supported_genres():
    """Get list of supported genres"""
    music_generator = MusicGenerator()
    return {"genres": music_generator.get_supported_genres()}


@router.get("/metadata/voice-types")
def get_supported_voice_types():
    """Get list of supported voice types"""
    music_generator = MusicGenerator()
    return {"voice_types": music_generator.get_supported_voice_types()}


@router.get("/metadata/styles")
def get_supported_styles():
    """Get list of supported styles"""
    music_generator = MusicGenerator()
    return {"styles": music_generator.get_supported_styles()}
