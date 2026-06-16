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
    postgis_schema: str = "lftr"
    spatial_mode: str = "mock"
    spatial_tile_deg: float = 1.0
    geometry_simplify_global: float = 0.2
    geometry_simplify_regional: float = 0.05
    geometry_simplify_local: float = 0.005
    mock_stream_fps: float = 1.0
    target_stream_fps: str = "5-10"
    provider_mode: str = "hybrid"
    gfs_enabled: bool = False
    gfs_ncss_base_url: str = "https://thredds.ucar.edu/thredds/ncss/grib/NCEP/GFS/Global_0p25deg/latest.xml"
    gfs_timeout_seconds: float = 8.0
    gfs_ttl_seconds: int = 900
    gfs_max_grid_points: int = 256
    gfs_cache_dir: str = ".cache/gfs"
    rtofs_enabled: bool = False
    rtofs_nomads_base: str = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod"
    rtofs_timeout_seconds: float = 8.0
    rtofs_ttl_seconds: int = 900
    rtofs_cache_dir: str = ".cache/rtofs"
    rtofs_depth_levels: str = "surface"
    rtofs_max_grid_points: int = 256
    rtofs_provider_mode: str = "hybrid"
    chl_enabled: bool = False
    chl_provider: str = "disabled"
    chl_erddap_base: str = "https://coastwatch.pfeg.noaa.gov/erddap"
    chl_dataset_id: str = ""
    chl_ttl_seconds: int = 21600
    chl_cache_dir: str = "data/cache/chlorophyll"
    usgs_enabled: bool = False
    usgs_source_family: str = "mock"
    usgs_cache_dir: str = "data/cache/usgs"
    usgs_timeout_seconds: float = 30.0
    usgs_max_features: int = 5000
    usgs_min_area_km2_global: float = 5.0
    usgs_min_area_km2_regional: float = 0.25
    usgs_min_area_km2_local: float = 0.01
    usgs_simplify_global: float = 0.01
    usgs_simplify_regional: float = 0.0025
    usgs_simplify_local: float = 0.0005
    usgs_arcgis_url: str = ""
    usgs_arcgis_layer: str = ""
    usgs_geojson_path: str = ""
    usgs_shapefile_zip_path: str = ""
    usgs_default_bbox: str = "-125,32,-117,38"
    lightning_enabled: bool = False
    lightning_provider: str = "mock"
    lightning_ttl_seconds: int = 120
    lightning_max_flashes: int = 50
    lightning_cache_dir: str = "data/cache/lightning"
    broadcast_default_room: str = "default"
    broadcast_max_message_chars: int = 2000
    broadcast_uploads_enabled: bool = False
    broadcast_upload_dir: str = "data/uploads/broadcast"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LFTR_")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
