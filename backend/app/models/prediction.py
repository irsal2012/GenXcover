from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class PopularityPrediction(Base):
    __tablename__ = "popularity_predictions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Prediction results
    popularity_score = Column(Float, nullable=False)  # 0-100 scale
    confidence_score = Column(Float, nullable=False)  # 0-1 scale
    
    # Analysis breakdown
    audio_analysis = Column(JSON, nullable=True)  # Audio features analysis
    lyrics_analysis = Column(JSON, nullable=True)  # Lyrics sentiment, themes, etc.
    market_analysis = Column(JSON, nullable=True)  # Market trends, timing, etc.
    
    # Detailed predictions
    genre_fit_score = Column(Float, nullable=True)
    trend_alignment_score = Column(Float, nullable=True)
    catchiness_score = Column(Float, nullable=True)
    commercial_appeal_score = Column(Float, nullable=True)
    
    # Recommendations
    improvement_suggestions = Column(JSON, nullable=True)
    target_demographics = Column(JSON, nullable=True)
    optimal_release_timing = Column(JSON, nullable=True)
    
    # Model information
    model_version = Column(String, nullable=False)
    analysis_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    song = relationship("Song", back_populates="predictions")
    user = relationship("User", back_populates="predictions")
