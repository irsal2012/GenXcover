import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GenXcover API"
    version: str = "1.0.0"
    debug: bool = True
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./genxcover.db"
    
    # CORS
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ]
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys (optional)
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-ada-002"
    tavily_api_key: str = ""
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = ""
    azure_openai_max_tokens: str = "4000"
    azure_openai_temperature: str = "0.7"
    
    # Search Configuration
    max_search_results: int = 100
    default_search_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
