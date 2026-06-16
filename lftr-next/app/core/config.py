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
    provider_mode: str = "hybrid"
    gfs_enabled: bool = False
    gfs_ncss_base_url: str = "https://thredds.ucar.edu/thredds/ncss/grib/NCEP/GFS/Global_0p25deg/latest.xml"
    gfs_timeout_seconds: float = 8.0
    gfs_ttl_seconds: int = 900
    gfs_max_grid_points: int = 256
    gfs_cache_dir: str = ".cache/gfs"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LFTR_")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
