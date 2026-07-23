"""Load/save user settings and challenge progress."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def user_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        path = Path(base) / "Cipher"
    else:
        path = Path.home() / ".cipher"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class Settings:
    master_volume: float = 0.85
    music_volume: float = 0.55
    sfx_volume: float = 0.8
    fullscreen: bool = True
    last_arena: str = "neon_sphere"
    last_difficulty: str = "Operative"
    show_fps: bool = False

    def clamp(self) -> None:
        self.master_volume = max(0.0, min(1.0, float(self.master_volume)))
        self.music_volume = max(0.0, min(1.0, float(self.music_volume)))
        self.sfx_volume = max(0.0, min(1.0, float(self.sfx_volume)))

    def effective_music(self) -> float:
        return self.master_volume * self.music_volume

    def effective_sfx(self) -> float:
        return self.master_volume * self.sfx_volume


@dataclass
class Progress:
    challenge_index: int = 0
    best_streak: int = 0
    unlocked_max: int = 0


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        backup = path.with_suffix(path.suffix + ".bak")
        try:
            path.replace(backup)
        except OSError:
            pass
    return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def load_settings() -> Settings:
    path = user_data_dir() / "settings.json"
    raw = _read_json(path)
    s = Settings()
    if raw:
        for k in (
            "master_volume",
            "music_volume",
            "sfx_volume",
            "fullscreen",
            "last_arena",
            "last_difficulty",
            "show_fps",
        ):
            if k in raw:
                setattr(s, k, raw[k])
    s.clamp()
    return s


def save_settings(settings: Settings) -> None:
    settings.clamp()
    _write_json(user_data_dir() / "settings.json", asdict(settings))


def load_progress() -> Progress:
    path = user_data_dir() / "progress.json"
    raw = _read_json(path)
    p = Progress()
    if raw:
        for k in ("challenge_index", "best_streak", "unlocked_max"):
            if k in raw:
                setattr(p, k, int(raw[k]))
    return p


def save_progress(progress: Progress) -> None:
    _write_json(user_data_dir() / "progress.json", asdict(progress))
