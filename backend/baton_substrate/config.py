from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: Literal["local", "production"] = "local"
    database_url: str = (
        f"sqlite+aiosqlite:///{Path(__file__).resolve().parent.parent / 'baton.sqlite'}"
    )
    host: str = "0.0.0.0"
    port: int = 8787
    baton_lease_ms: int = Field(default=20_000, gt=0, le=300_000)
    default_energy_budget: int = Field(default=1000, gt=0)
    api_key: str = ""
    api_keys: str = ""
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3100",
        "http://127.0.0.1:3100",
        "http://localhost:8787",
        "http://127.0.0.1:8787",
    ]
    max_mission_pack_bytes: int = Field(default=5_000_000, gt=0)
    event_page_limit_max: int = Field(default=500, gt=0, le=5_000)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = {"env_prefix": "BATON_"}


settings = Settings()
