"""Color helpers."""
from __future__ import annotations

from cipher.constants import (
    BG_DEEP,
    CYAN,
    DANGER,
    ELEC_BLUE,
    GREEN,
    GRID,
    HOT_PINK,
    MAGENTA,
    ORANGE,
    PURPLE,
    WHITE_GLOW,
    YELLOW,
)


def with_alpha(color: tuple[int, ...], alpha: int) -> tuple[int, int, int, int]:
    r, g, b = color[:3]
    return r, g, b, max(0, min(255, alpha))


def darken(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        max(0, int(color[0] * factor)),
        max(0, int(color[1] * factor)),
        max(0, int(color[2] * factor)),
    )


def lighten(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        min(255, int(color[0] + (255 - color[0]) * factor)),
        min(255, int(color[1] + (255 - color[1]) * factor)),
        min(255, int(color[2] + (255 - color[2]) * factor)),
    )


def lerp_color(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


POWERUP_COLORS = {
    "speed": YELLOW,
    "multiball": WHITE_GLOW,
    "gravity": PURPLE,
    "shield": CYAN,
    "overdrive": MAGENTA,
}

__all__ = [
    "BG_DEEP",
    "CYAN",
    "MAGENTA",
    "PURPLE",
    "HOT_PINK",
    "ELEC_BLUE",
    "WHITE_GLOW",
    "GRID",
    "DANGER",
    "YELLOW",
    "ORANGE",
    "GREEN",
    "with_alpha",
    "darken",
    "lighten",
    "lerp_color",
    "POWERUP_COLORS",
]
