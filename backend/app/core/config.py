from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "GenXcover"
    version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./genxcover.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # OpenAI (Legacy - keeping for backward compatibility)
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-ada-002"
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_max_tokens: int = 4000
    azure_openai_temperature: float = 0.7
    
    # Tavily (for search)
    tavily_api_key: Optional[str] = None
    
    # Search Configuration
    max_search_results: int = 100
    default_search_timeout: int = 30
    
    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # Audio Processing
    sample_rate: int = 44100
    audio_format: str = "wav"
    
    # CORS
    backend_cors_origins: list = [
        "http://localhost:3000",  # React web app
        "http://localhost:19006",  # React Native web
        "exp://localhost:19000",  # Expo
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
