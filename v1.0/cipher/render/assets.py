"""Load packaged Imagine-generated pixel art assets.

Assets live in cipher/assets/ and are bundled into the PyInstaller build.
Falls back to procedural sprites if a file is missing.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import pygame


def asset_dir() -> Path:
    # PyInstaller onefile extracts to sys._MEIPASS
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS) / "cipher" / "assets"
        if base.is_dir():
            return base
    # Dev: package-relative
    here = Path(__file__).resolve().parent.parent / "assets"
    return here


def asset_path(name: str) -> Path:
    return asset_dir() / name


@lru_cache(maxsize=128)
def load_image(name: str) -> pygame.Surface | None:
    path = asset_path(name)
    if not path.exists():
        return None
    try:
        surf = pygame.image.load(str(path)).convert_alpha()
        return surf
    except pygame.error:
        return None


def clear_asset_cache() -> None:
    load_image.cache_clear()


def has_baked_assets() -> bool:
    return asset_path("vex_idle.png").exists() and asset_path("ball.png").exists()
