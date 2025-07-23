from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime

router = APIRouter()

# Simple in-memory storage for demo purposes
songs_storage = []

@router.post("/generate")
async def generate_song(request: Dict[str, Any]):
    """
    Simple song generation endpoint that returns a mock response
    until ML dependencies are properly installed
    """
    try:
        title = request.get("title", "Untitled Song")
        genre = request.get("genre", "pop")
        lyrics = request.get("lyrics", "")
        
        # Create a mock song response
        song_id = len(songs_storage) + 1
        song_data = {
            "id": song_id,
            "title": title,
            "genre": genre,
            "lyrics": lyrics,
            "status": "generated",
            "created_at": datetime.now().isoformat(),
            "audio_url": None,  # Would be populated when ML is working
            "midi_url": None,   # Would be populated when ML is working
            "message": "Song generation is temporarily disabled. ML dependencies need to be installed."
        }
        
        songs_storage.append(song_data)
        
        return {
            "success": True,
            "song": song_data,
            "message": "Mock song created successfully. Full generation will be available once ML dependencies are installed."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating song: {str(e)}")

@router.get("/")
async def list_songs():
    """List all generated songs"""
    return {
        "success": True,
        "songs": songs_storage,
        "total": len(songs_storage)
    }

@router.get("/{song_id}")
async def get_song(song_id: int):
    """Get a specific song by ID"""
    for song in songs_storage:
        if song["id"] == song_id:
            return {
                "success": True,
                "song": song
            }
    
    raise HTTPException(status_code=404, detail="Song not found")

@router.delete("/{song_id}")
async def delete_song(song_id: int):
    """Delete a song by ID"""
    global songs_storage
    original_length = len(songs_storage)
    songs_storage = [song for song in songs_storage if song["id"] != song_id]
    
    if len(songs_storage) < original_length:
        return {
            "success": True,
            "message": f"Song {song_id} deleted successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Song not found")

@router.get("/status/ml")
async def ml_status():
    """Check ML dependencies status"""
    return {
        "ml_available": False,
        "message": "ML dependencies (torch, audiocraft, etc.) are not installed",
        "required_packages": [
            "torch",
            "torchaudio", 
            "transformers",
            "audiocraft",
            "librosa",
            "scipy",
            "soundfile"
        ],
        "install_command": "pip install torch torchaudio transformers audiocraft librosa scipy soundfile"
    }
