from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel


class ProviderStatus(BaseModel):
    provider: str
    mode: str
    enabled: bool
    live_ok: bool = False
    cache_hit: bool = False
    degraded: bool = False
    valid_time: str | None = None
    generated_time: str
    error: str | None = None
    details: dict[str, Any] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
