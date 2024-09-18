from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    db_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()