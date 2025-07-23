from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SongBase(BaseModel):
    title: str
    genre: str
    style: Optional[str] = None
    theme: Optional[str] = None
    voice_type: Optional[str] = None


class SongCreate(SongBase):
    lyrics: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None


class SongUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None
    theme: Optional[str] = None
    voice_type: Optional[str] = None
    lyrics: Optional[str] = None
    is_public: Optional[bool] = None


class SongGenerate(BaseModel):
    title: str
    genre: str
    style: Optional[str] = None
    theme: Optional[str] = None
    voice_type: Optional[str] = None
    custom_prompt: Optional[str] = None
    include_audio: bool = True
    include_midi: bool = True


class SongInDBBase(SongBase):
    id: int
    lyrics: Optional[str] = None
    audio_file_path: Optional[str] = None
    midi_file_path: Optional[str] = None
    cover_image_path: Optional[str] = None
    duration: Optional[float] = None
    tempo: Optional[float] = None
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    audio_features: Optional[Dict[str, Any]] = None
    generation_params: Optional[Dict[str, Any]] = None
    is_generated: bool = False
    is_public: bool = True
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Song(SongInDBBase):
    pass


class SongWithCreator(Song):
    creator: Optional[Dict[str, Any]] = None


class SongList(BaseModel):
    songs: list[Song]
    total: int
    page: int
    per_page: int
