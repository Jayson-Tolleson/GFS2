from __future__ import annotations

import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any
from app.core.config import get_settings
from app.fields.ocean import build_mock_ocean_frame, derive_bait_score, enrich_ocean_diagnostics
from app.fields.base import OceanFieldFrame
from app.providers.provider_status import ProviderStatus, now_iso
from app.providers.rtofs_aliases import aliases_used
from app.providers.rtofs_cache import RTOFSCache
from app.schemas.scene import BBox

RTOFS_PROVIDER_NAME = "rtofs_ncep"


def parse_depth_levels(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def build_rtofs_url(base_url: str, bbox: BBox, depth_levels: list[str], max_points: int) -> str:
    query: dict[str, str] = {
        "bbox": f"{bbox.west},{bbox.south},{bbox.east},{bbox.north}",
        "depth": ";".join(depth_levels),
        "max_points": str(max_points),
        "vars": ",".join(alias[0] for alias in aliases_used().values()),
    }
    return f"{base_url}?{urllib.parse.urlencode(query)}"


def cache_key(bbox: BBox, depth_levels: list[str]) -> str:
    depth = "_".join(depth_levels)
    return f"rtofs_ocean_{bbox.west:.2f}_{bbox.south:.2f}_{bbox.east:.2f}_{bbox.north:.2f}_{depth}"


def frame_to_cache_payload(frame: OceanFieldFrame, status: ProviderStatus) -> dict[str, Any]:
    return {"frame": frame.model_dump(mode="json"), "status": status.model_dump(mode="json")}


def frame_from_cache_payload(payload: dict[str, Any]) -> tuple[OceanFieldFrame, ProviderStatus]:
    return OceanFieldFrame(**payload["frame"]), ProviderStatus(**payload["status"])


class RTOFSNCEPProvider:
    name = RTOFS_PROVIDER_NAME

    def __init__(self) -> None:
        self.settings = get_settings()
        self.depth_levels = parse_depth_levels(self.settings.rtofs_depth_levels)
        self.cache = RTOFSCache(self.settings.rtofs_cache_dir)

    def status(self) -> ProviderStatus:
        return ProviderStatus(
            provider=self.name,
            mode=self.settings.rtofs_provider_mode,
            enabled=self.settings.rtofs_enabled,
            generated_time=now_iso(),
            degraded=not self.settings.rtofs_enabled or self.settings.rtofs_provider_mode == "mock",
            details={
                "base_url": self.settings.rtofs_nomads_base,
                "ttl_seconds": self.settings.rtofs_ttl_seconds,
                "max_grid_points": self.settings.rtofs_max_grid_points,
                "depth_levels": self.depth_levels,
                "sample_interface": "sample(lon, lat, depth_m, time)",
            },
        )

    def fetch_ocean(self, bbox: BBox) -> tuple[OceanFieldFrame, ProviderStatus]:
        mode = self.settings.rtofs_provider_mode
        if mode == "mock" or not self.settings.rtofs_enabled:
            return self._mock_frame(bbox, reason="mock mode" if mode == "mock" else "RTOFS disabled")
        try:
            return self._live_frame(bbox)
        except Exception as exc:
            cached = self._last_good(bbox, str(exc))
            if cached:
                return cached
            return self._mock_frame(bbox, reason=f"live RTOFS failed and no cache exists: {exc}")

    def sample(self, lon: float, lat: float, depth_m: float = 0, time: str | None = None) -> dict[str, float | str | None]:
        # Interface-ready placeholder for future 3D truth sampling from cached/live RTOFS cubes.
        return {"lon": lon, "lat": lat, "depth_m": depth_m, "time": time, "status": "placeholder"}

    def _live_frame(self, bbox: BBox) -> tuple[OceanFieldFrame, ProviderStatus]:
        url = build_rtofs_url(self.settings.rtofs_nomads_base, bbox, self.depth_levels, self.settings.rtofs_max_grid_points)
        # TODO: add bounded NOMADS/NetCDF subset parsing; never download giant whole-world files in request paths.
        with urllib.request.urlopen(url, timeout=self.settings.rtofs_timeout_seconds) as response:
            response.read(256)
        frame = self._build_provider_frame(bbox)
        frame.metadata.update(self._metadata(bbox, url, live_ok=True, cache_status="live"))
        status = self._status_from_frame(frame, live_ok=True, cache_hit=False, degraded=False, source=url)
        self.cache.save(cache_key(bbox, self.depth_levels), frame_to_cache_payload(frame, status))
        return frame, status

    def _last_good(self, bbox: BBox, error: str) -> tuple[OceanFieldFrame, ProviderStatus] | None:
        payload = self.cache.load(cache_key(bbox, self.depth_levels))
        if not payload:
            return None
        frame, status = frame_from_cache_payload(payload)
        status.cache_hit = True
        status.live_ok = False
        status.degraded = True
        status.error = error
        status.generated_time = now_iso()
        frame.metadata.update({"cache_status": "last_good", "live_ok": False, "degraded": True, "error": error})
        return frame, status

    def _mock_frame(self, bbox: BBox, reason: str) -> tuple[OceanFieldFrame, ProviderStatus]:
        frame = self._build_provider_frame(bbox)
        frame.metadata.update(self._metadata(bbox, "mock:rtofs_ncep", live_ok=False, cache_status="mock", degraded=True, error=reason))
        return frame, self._status_from_frame(frame, live_ok=False, cache_hit=False, degraded=True, source="mock:rtofs_ncep", error=reason)

    def _build_provider_frame(self, bbox: BBox) -> OceanFieldFrame:
        frame = build_mock_ocean_frame(bbox, depth_levels=self.depth_levels)
        enrich_ocean_diagnostics(frame)
        frame.channels["bait_score"] = derive_bait_score(frame.channels)
        return frame

    def _metadata(self, bbox: BBox, source: str, live_ok: bool, cache_status: str, degraded: bool = False, error: str | None = None) -> dict[str, Any]:
        return {
            "provider": self.name,
            "source": source,
            "requested_bbox": bbox.model_dump(),
            "resolved_bbox": bbox.model_dump(),
            "valid_time": datetime.now(timezone.utc).isoformat(),
            "generated_time": now_iso(),
            "variable_aliases": aliases_used(),
            "grid_shape": [4, 4],
            "depth_levels": self.depth_levels,
            "current_units": "m/s eastward/northward components; speed m/s; direction degrees from east counterclockwise",
            "cache_status": cache_status,
            "live_ok": live_ok,
            "degraded": degraded,
            "error": error,
            "chlorophyll_hook": "future booster; not required for bait_score",
        }

    def _status_from_frame(self, frame: OceanFieldFrame, live_ok: bool, cache_hit: bool, degraded: bool, source: str, error: str | None = None) -> ProviderStatus:
        return ProviderStatus(
            provider=self.name,
            mode=self.settings.rtofs_provider_mode,
            enabled=self.settings.rtofs_enabled,
            live_ok=live_ok,
            cache_hit=cache_hit,
            degraded=degraded,
            valid_time=frame.valid_time,
            generated_time=now_iso(),
            error=error,
            details={"source": source, "variable_aliases": aliases_used(), "grid_shape": list(frame.grid_shape), "depth_levels": frame.depth_levels},
        )


def get_rtofs_provider() -> RTOFSNCEPProvider:
    return RTOFSNCEPProvider()
