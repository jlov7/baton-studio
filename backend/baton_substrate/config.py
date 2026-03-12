from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        f"sqlite+aiosqlite:///{Path(__file__).resolve().parent.parent / 'baton.sqlite'}"
    )
    host: str = "0.0.0.0"
    port: int = 8787
    baton_lease_ms: int = 20_000
    default_energy_budget: int = 1000

    model_config = {"env_prefix": "BATON_"}


settings = Settings()
