from functools import lru_cache
import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Plataforma RRHH"
    app_env: str = "development"
    secret_key: str = "dev-insecure-secret-key"
    access_token_expire_minutes: int = 720
    backend_cors_origins: str | List[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./rrhh.db"
    public_base_url: str = "http://localhost:5173"
    upload_dir: str = "uploads"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        raw = value.strip()
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in value.split(",") if item.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
