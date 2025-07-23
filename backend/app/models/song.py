from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False)
    style = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    voice_type = Column(String, nullable=True)
    
    # Content
    lyrics = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
    midi_file_path = Column(String, nullable=True)
    cover_image_path = Column(String, nullable=True)
    
    # Metadata
    duration = Column(Float, nullable=True)  # in seconds
    tempo = Column(Float, nullable=True)  # BPM
    key_signature = Column(String, nullable=True)
    time_signature = Column(String, nullable=True)
    
    # Audio features for analysis
    audio_features = Column(JSON, nullable=True)  # Store librosa analysis results
    
    # Generation settings
    generation_params = Column(JSON, nullable=True)
    
    # Status
    is_generated = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="songs")
    recordings = relationship("Recording", back_populates="song")
    predictions = relationship("PopularityPrediction", back_populates="song")
