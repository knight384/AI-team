from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/mydb"
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    jwt_secret: str = "your-super-secret-jwt-key-here"
    
    # External APIs
    openai_api_key: str = ""
    
    # Application
    api_version: str = "v1"
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()