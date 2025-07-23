from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # File paths
    audio_file_path = Column(String, nullable=False)
    waveform_data_path = Column(String, nullable=True)
    
    # Recording metadata
    duration = Column(Float, nullable=True)  # in seconds
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    bit_depth = Column(Integer, nullable=True)
    
    # Recording settings
    effects_applied = Column(JSON, nullable=True)  # List of effects and their parameters
    recording_settings = Column(JSON, nullable=True)
    
    # Multi-track support
    track_number = Column(Integer, default=1)
    is_master_track = Column(Boolean, default=True)
    parent_recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=True)
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=True)  # Optional link to generated song
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recordings")
    song = relationship("Song", back_populates="recordings")
    child_tracks = relationship("Recording", backref="parent_track", remote_side=[id])
