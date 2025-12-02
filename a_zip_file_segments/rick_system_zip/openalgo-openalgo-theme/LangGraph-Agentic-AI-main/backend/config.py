# backend/config.py
from typing import Optional
from sqlalchemy import create_engine
from typing import ClassVar
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = 'postgresql://postgres:password@localhost:5432/agentic_trading'
    # Use 'postgres' as host for Docker Compose networking

    # Redis
    redis_url: str = "redis://redis:6379"
    # Use 'redis' as host and default port 6379 for Docker Compose networking

    # API Keys
    tavily_api_key: Optional[str] = None
    next_public_polygon_api_key: Optional[str] = None
    next_public_finnhub_websocket_key: Optional[str] = None
    next_public_finnhub_api_key: Optional[str] = None
    next_public_marketstack_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_application_credentials: Optional[str] = None
    next_public_alpha_vantage_api_key: Optional[str] = None
    sportmonks_api_token: Optional[str] = None
    gemini_api_key: Optional[str] = None
    sunbet_url: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_api_url: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Agent ports
    chartanalyst_port: int = 8001
    riskmanager_port: int = 8002
    marketsentinel_port: int = 8003
    macroforecaster_port: int = 8004
    tacticbot_port: int = 8005
    platformpilot_port: int = 8006

    # Orchestrator
    orchestrator_port: int = 8007

    class Config:
        env_file = ".env"

settings = Settings()
