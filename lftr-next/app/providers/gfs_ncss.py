from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any
from app.core.config import get_settings
from app.fields.atmosphere import build_mock_atmosphere_frame
from app.fields.base import AtmosphereFieldFrame
from app.providers.provider_status import ProviderStatus, now_iso
from app.schemas.scene import BBox
from app.services.provider_cache import ProviderCache

GFS_VARIABLES = [
    'Temperature_height_above_ground',
    'Relative_humidity_height_above_ground',
    'Dewpoint_temperature_height_above_ground',
    'Pressure_reduced_to_MSL_msl',
    'Total_cloud_cover_entire_atmosphere',
    'Low_cloud_cover_low_cloud',
    'Medium_cloud_cover_middle_cloud',
    'High_cloud_cover_high_cloud',
    'Precipitation_rate_surface',
    'u-component_of_wind_height_above_ground',
    'v-component_of_wind_height_above_ground',
]


def bbox_query_params(bbox: BBox) -> dict[str, str]:
    return {'west': str(bbox.west), 'east': str(bbox.east), 'south': str(bbox.south), 'north': str(bbox.north)}


def build_ncss_url(base_url: str, bbox: BBox, max_points: int) -> str:
    query: dict[str, str | list[str]] = {
        **bbox_query_params(bbox),
        'time': 'present',
        'accept': 'netcdf4',
        'addLatLon': 'true',
        'maxx': str(max_points),
        'var': GFS_VARIABLES,
    }
    return f'{base_url}?{urllib.parse.urlencode(query, doseq=True)}'


def cache_key(bbox: BBox) -> str:
    return f'gfs_atmosphere_{bbox.west:.2f}_{bbox.south:.2f}_{bbox.east:.2f}_{bbox.north:.2f}'


def frame_to_cache_payload(frame: AtmosphereFieldFrame, status: ProviderStatus) -> dict[str, Any]:
    return {'frame': frame.model_dump(mode='json'), 'status': status.model_dump(mode='json')}


def frame_from_cache_payload(payload: dict[str, Any]) -> tuple[AtmosphereFieldFrame, ProviderStatus]:
    return AtmosphereFieldFrame(**payload['frame']), ProviderStatus(**payload['status'])


class GFSNCSSProvider:
    name = 'gfs_ncss'

    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = ProviderCache(self.settings.gfs_cache_dir)

    def status(self) -> ProviderStatus:
        return ProviderStatus(
            provider=self.name,
            mode=self.settings.provider_mode,
            enabled=self.settings.gfs_enabled,
            generated_time=now_iso(),
            degraded=not self.settings.gfs_enabled or self.settings.provider_mode == 'mock',
            details={
                'base_url': self.settings.gfs_ncss_base_url,
                'ttl_seconds': self.settings.gfs_ttl_seconds,
                'max_grid_points': self.settings.gfs_max_grid_points,
            },
        )

    def fetch_atmosphere(self, bbox: BBox) -> tuple[AtmosphereFieldFrame, ProviderStatus]:
        mode = self.settings.provider_mode
        if mode == 'mock' or not self.settings.gfs_enabled:
            return self._mock_frame(bbox, reason='mock mode' if mode == 'mock' else 'GFS disabled')
        try:
            return self._live_frame(bbox)
        except Exception as exc:  # provider boundary must never crash callers
            cached = self._last_good(bbox, str(exc))
            if cached:
                return cached
            return self._mock_frame(bbox, reason=f'live GFS failed and no cache exists: {exc}')

    def _live_frame(self, bbox: BBox) -> tuple[AtmosphereFieldFrame, ProviderStatus]:
        url = build_ncss_url(self.settings.gfs_ncss_base_url, bbox, self.settings.gfs_max_grid_points)
        # TODO: implement real bounded NCSS NetCDF parsing with xarray/netCDF4.
        # Current live path is only a reachability probe/live_stub and returns mock-shaped fields.
        with urllib.request.urlopen(url, timeout=self.settings.gfs_timeout_seconds) as response:
            response.read(256)
        frame = build_mock_atmosphere_frame(bbox)
        frame.metadata.update(self._metadata(bbox, url, live_ok=True, cache_status='live'))
        status = self._status_from_frame(frame, live_ok=True, cache_hit=False, degraded=False, source=url)
        self.cache.save(cache_key(bbox), frame_to_cache_payload(frame, status))
        return frame, status

    def _last_good(self, bbox: BBox, error: str) -> tuple[AtmosphereFieldFrame, ProviderStatus] | None:
        payload = self.cache.load(cache_key(bbox))
        if not payload:
            return None
        frame, status = frame_from_cache_payload(payload)
        status.cache_hit = True
        status.live_ok = False
        status.degraded = True
        status.error = error
        status.generated_time = now_iso()
        frame.metadata.update({'cache_status': 'last_good', 'live_ok': False, 'degraded': True, 'error': error})
        return frame, status

    def _mock_frame(self, bbox: BBox, reason: str) -> tuple[AtmosphereFieldFrame, ProviderStatus]:
        frame = build_mock_atmosphere_frame(bbox)
        frame.metadata.update(self._metadata(bbox, 'mock:gfs_ncss', live_ok=False, cache_status='mock', degraded=True, error=reason))
        return frame, self._status_from_frame(frame, live_ok=False, cache_hit=False, degraded=True, source='mock:gfs_ncss', error=reason)

    def _metadata(self, bbox: BBox, source: str, live_ok: bool, cache_status: str, degraded: bool = False, error: str | None = None) -> dict[str, Any]:
        return {
            'provider': self.name,
            'source': source,
            'requested_bbox': bbox.model_dump(),
            'resolved_bbox': bbox.model_dump(),
            'valid_time': datetime.now(timezone.utc).isoformat(),
            'generated_time': now_iso(),
            'variables': GFS_VARIABLES,
            'grid_shape': [4, 4],
            'provider_id': 'gfs_ncss_atmosphere',
            'source_url': source,
            'configured_base_url': self.settings.gfs_ncss_base_url,
            'request_url_example': build_ncss_url(self.settings.gfs_ncss_base_url, bbox, self.settings.gfs_max_grid_points),
            'variables_requested': GFS_VARIABLES,
            'normalized_channels': ['cloud_density', 'rain_rate', 'wind_u', 'wind_v', 'humidity', 'temperature', 'pressure'],
            'units': {'wind_u': 'm/s eastward', 'wind_v': 'm/s northward'},
            'parser_status': 'adapter_probe_stub_netCDF_parser_TODO',
            'live_status': 'live_stub' if live_ok else 'mock_fallback',
            'cache_status': cache_status,
            'live_ok': live_ok,
            'degraded': degraded,
            'error': error,
        }

    def _status_from_frame(self, frame: AtmosphereFieldFrame, live_ok: bool, cache_hit: bool, degraded: bool, source: str, error: str | None = None) -> ProviderStatus:
        return ProviderStatus(
            provider=self.name,
            mode=self.settings.provider_mode,
            enabled=self.settings.gfs_enabled,
            live_ok=live_ok,
            cache_hit=cache_hit,
            degraded=degraded,
            valid_time=frame.valid_time,
            generated_time=now_iso(),
            error=error,
            details={'source': source, 'variables': GFS_VARIABLES, 'grid_shape': list(frame.grid_shape)},
        )


def get_gfs_provider() -> GFSNCSSProvider:
    return GFSNCSSProvider()
