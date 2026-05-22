from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "VoiceAgent")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./voice_agent.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")

settings = Settings()