"""Math helpers — pure functions, easy to unit test."""
from __future__ import annotations

import math
from typing import Sequence


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def inv_lerp(a: float, b: float, v: float) -> float:
    if abs(b - a) < 1e-9:
        return 0.0
    return (v - a) / (b - a)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = clamp(inv_lerp(edge0, edge1, x), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def length(x: float, y: float) -> float:
    return math.hypot(x, y)


def normalize(x: float, y: float) -> tuple[float, float]:
    mag = math.hypot(x, y)
    if mag < 1e-8:
        return 0.0, 0.0
    return x / mag, y / mag


def dot(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * bx + ay * by


def reflect(vx: float, vy: float, nx: float, ny: float) -> tuple[float, float]:
    """Reflect velocity off a unit normal."""
    d = 2.0 * dot(vx, vy, nx, ny)
    return vx - d * nx, vy - d * ny


def approach(current: float, target: float, max_delta: float) -> float:
    if current < target:
        return min(current + max_delta, target)
    return max(current - max_delta, target)


def angle_to(dx: float, dy: float) -> float:
    return math.atan2(dy, dx)


def from_angle(angle: float, mag: float = 1.0) -> tuple[float, float]:
    return math.cos(angle) * mag, math.sin(angle) * mag


def dist(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(bx - ax, by - ay)


def circles_overlap(
    ax: float, ay: float, ar: float, bx: float, by: float, br: float
) -> bool:
    r = ar + br
    return (bx - ax) ** 2 + (by - ay) ** 2 <= r * r


def point_in_rect(px: float, py: float, rect: Sequence[float]) -> bool:
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def rects_overlap(a: Sequence[float], b: Sequence[float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
