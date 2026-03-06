from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from ..core.settings import settings


class JsonStore:
    _locks: dict[str, Lock] = {}

    def __init__(self, name: str) -> None:
        self.path = Path(settings.store_dir)
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / f'{name}.json'
        self.lock = self._locks.setdefault(name, Lock())

    def read(self) -> list[dict[str, Any]]:
        if not self.file.exists():
            return []
        with self.lock:
            try:
                return json.loads(self.file.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                return []

    def write(self, data: list[dict[str, Any]]) -> None:
        with self.lock:
            self.file.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding='utf-8')
