import json
from pathlib import Path
from typing import Any


class ProviderCache:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        safe = ''.join(char if char.isalnum() or char in '-_' else '_' for char in key)
        return self.cache_dir / f'{safe}.json'

    def load(self, key: str) -> dict[str, Any] | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding='utf-8'))

    def save(self, key: str, payload: dict[str, Any]) -> None:
        self.path_for(key).write_text(json.dumps(payload), encoding='utf-8')
