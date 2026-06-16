from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LFTR Next"
    host: str = "0.0.0.0"
    port: int = 8787
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    google_maps_api_key: str = ""
    postgis_dsn: str | None = None
    postgis_enabled: bool = False
    mock_stream_fps: float = 1.0
    target_stream_fps: str = "5-10"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LFTR_")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
