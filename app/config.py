import os
from pydantic_settings import BaseSettings

# Calculate path to .env file (one level up from app/config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ENV_PATH

settings = Settings()
