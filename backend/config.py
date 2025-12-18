"""
Configuration module for the AI Financial Analyst backend.
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # LLM Settings
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.3
    max_tokens: int = 4096
    
    # Market Data Settings
    default_period: str = "1y"  # Default historical data period
    cache_ttl: int = 300  # Cache TTL in seconds (5 minutes)
    
    class Config:
        env_file = ".env"


settings = Settings()
