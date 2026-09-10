from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str = "postgresql+psycopg://nirikshan:change-me-in-local-env@localhost:5432/nirikshan"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    risk_weights_path: str = "config/risk_weights.yaml"
    app_name: str = "NIRIKSHAN"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    def resolved_weights_path(self) -> Path:
        path = Path(self.risk_weights_path)
        if path.is_file():
            return path
        repo_root = Path(__file__).resolve().parents[2]
        candidate = repo_root / self.risk_weights_path
        if candidate.is_file():
            return candidate
        docker_path = Path("/config/risk_weights.yaml")
        if docker_path.is_file():
            return docker_path
        raise FileNotFoundError(f"Risk weights file not found: {self.risk_weights_path}")


@lru_cache
def get_settings() -> Settings:
    return Settings()
