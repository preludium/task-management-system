from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Task Management API"
    APP_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/taskdb"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # API
    API_V1_STR: str = "/api"
    TEST_V1_STR: str = "/test"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # SSE Configuration
    SSE_HEARTBEAT_INTERVAL: int = 30  # seconds
    SSE_MAX_CONNECTIONS: int = 100
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 12
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()