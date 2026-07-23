"""Cipher Ball entity."""
from __future__ import annotations

from dataclasses import dataclass, field

from cipher.constants import (
    BALL_FRICTION,
    BALL_MAX_SPEED,
    BALL_RADIUS,
    BALL_WALL_RESTITUTION,
    CYAN,
)
from cipher.core.math_util import length
from cipher.gameplay.physics import apply_friction, clamp_speed, integrate
from cipher.render.fx import Trail


@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = BALL_RADIUS
    active: bool = True
    is_extra: bool = False
    life: float = 9999.0
    trail: Trail = field(default_factory=lambda: Trail(14))
    frame: int = 0

    def update(self, dt: float, max_speed: float | None = None) -> None:
        if not self.active:
            return
        if self.is_extra:
            self.life -= dt
            if self.life <= 0:
                self.active = False
                return
        self.x, self.y = integrate(self.x, self.y, self.vx, self.vy, dt)
        self.vx, self.vy = apply_friction(self.vx, self.vy, BALL_FRICTION, dt)
        cap = max_speed if max_speed is not None else BALL_MAX_SPEED
        self.vx, self.vy = clamp_speed(self.vx, self.vy, cap)
        self.trail.add(self.x, self.y)
        self.trail.update(dt)
        self.frame += 1

    @property
    def speed(self) -> float:
        return length(self.vx, self.vy)

    def reset(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.active = True
        self.trail = Trail(14)
        self.life = 9999.0
        self.is_extra = False

    def kick(self, kx: float, ky: float) -> None:
        self.vx += kx
        self.vy += ky
