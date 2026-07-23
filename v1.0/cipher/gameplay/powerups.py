"""Power-up spawns and effects."""
from __future__ import annotations

import random
from dataclasses import dataclass

from cipher.constants import (
    POWERUP_GRAVITY_DURATION,
    POWERUP_LIFETIME,
    POWERUP_MAX_ACTIVE,
    POWERUP_MULTIBALL_EXTRA_LIFE,
    POWERUP_OVERDRIVE_DURATION,
    POWERUP_RADIUS,
    POWERUP_SHIELD_DURATION,
    POWERUP_SPAWN_INTERVAL,
    POWERUP_SPEED_DURATION,
)
from cipher.core.math_util import dist

POWERUP_KINDS = ("speed", "multiball", "gravity", "shield", "overdrive")


@dataclass
class PowerUp:
    x: float
    y: float
    kind: str
    life: float = POWERUP_LIFETIME
    frame: int = 0
    radius: float = POWERUP_RADIUS

    @property
    def alive(self) -> bool:
        return self.life > 0


class PowerUpManager:
    def __init__(self, interval_mul: float = 1.0) -> None:
        self.items: list[PowerUp] = []
        self.timer = POWERUP_SPAWN_INTERVAL * 0.4
        self.interval = POWERUP_SPAWN_INTERVAL * interval_mul
        self.gravity_flip = False
        self.gravity_timer = 0.0
        self.spawn_points: list[tuple[float, float]] = []

    def set_spawn_points(self, points: list[tuple[float, float]]) -> None:
        self.spawn_points = points

    def update(self, dt: float) -> str | None:
        """Returns event name if something notable happened."""
        event = None
        if self.gravity_timer > 0:
            self.gravity_timer = max(0.0, self.gravity_timer - dt)
            if self.gravity_timer <= 0:
                self.gravity_flip = False

        for p in self.items:
            p.life -= dt
            p.frame += 1
        self.items = [p for p in self.items if p.alive]

        self.timer -= dt
        if self.timer <= 0 and len(self.items) < POWERUP_MAX_ACTIVE and self.spawn_points:
            self.timer = self.interval * random.uniform(0.85, 1.2)
            kind = random.choice(POWERUP_KINDS)
            # avoid stacking same spot
            for _ in range(8):
                x, y = random.choice(self.spawn_points)
                if all(dist(x, y, p.x, p.y) > 50 for p in self.items):
                    self.items.append(PowerUp(x, y, kind))
                    event = "spawn"
                    break
        return event

    def try_pickup(self, x: float, y: float, radius: float) -> PowerUp | None:
        for p in self.items:
            if dist(x, y, p.x, p.y) <= radius + p.radius:
                self.items.remove(p)
                return p
        return None

    def apply(self, kind: str, player, balls, arena_center: tuple[float, float]) -> str:
        """Apply effect; may mutate balls list. Returns effect tag."""
        if kind == "speed":
            player.give_speed(POWERUP_SPEED_DURATION)
            return "speed"
        if kind == "shield":
            player.give_shield(POWERUP_SHIELD_DURATION)
            return "shield"
        if kind == "overdrive":
            player.give_overdrive(POWERUP_OVERDRIVE_DURATION)
            return "overdrive"
        if kind == "gravity":
            self.gravity_flip = not self.gravity_flip
            self.gravity_timer = POWERUP_GRAVITY_DURATION
            return "gravity"
        if kind == "multiball":
            from cipher.gameplay.ball import Ball

            # spawn near player toward center
            cx, cy = arena_center
            dx, dy = cx - player.x, cy - player.y
            mag = (dx * dx + dy * dy) ** 0.5 or 1.0
            bx = player.x + dx / mag * 40
            by = player.y + dy / mag * 40
            b = Ball(bx, by, vx=dx / mag * 200, vy=dy / mag * 200, is_extra=True, life=POWERUP_MULTIBALL_EXTRA_LIFE)
            balls.append(b)
            return "multiball"
        return kind
