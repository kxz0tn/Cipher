"""Debris Field — moving asteroids and energy barriers."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from cipher.constants import ARENA_NAMES, HOT_PINK, PURPLE, YELLOW
from cipher.core.math_util import dist, normalize
from cipher.gameplay.arena import Arena, make_base_geometry
from cipher.gameplay.physics import resolve_circle_circle
from cipher.render.backgrounds import draw_debris_floor
from cipher.render.palette import with_alpha
from cipher.render.sprites import make_asteroid_sprite, make_barrier_sprite


@dataclass
class Asteroid:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    seed: int
    angle: float = 0.0
    spin: float = 0.5


@dataclass
class Barrier:
    x: float
    y: float
    w: float
    h: float
    active: bool = True
    timer: float = 0.0
    period: float = 3.0
    on_time: float = 1.8


class DebrisFieldArena(Arena):
    def __init__(self) -> None:
        bounds, left, right, ps, es, bs, pups = make_base_geometry()
        super().__init__(
            arena_id="debris_field",
            name=ARENA_NAMES["debris_field"],
            bounds=bounds,
            left_goal=left,
            right_goal=right,
            player_spawn=ps,
            enemy_spawn=es,
            ball_spawn=bs,
            powerup_spawns=pups,
            gravity_strength=0.0,
        )
        rng = random.Random(7)
        self.asteroids: list[Asteroid] = []
        for i in range(5):
            self.asteroids.append(
                Asteroid(
                    x=rng.uniform(bounds.left + 100, bounds.right - 100),
                    y=rng.uniform(bounds.top + 80, bounds.bottom - 80),
                    vx=rng.uniform(-40, 40),
                    vy=rng.uniform(-40, 40),
                    radius=rng.randint(16, 28),
                    seed=i + 1,
                    spin=rng.uniform(-1.2, 1.2),
                )
            )
        self.barriers = [
            Barrier(bounds.centerx - 20, bounds.top + 80, 40, 12, period=3.2, on_time=1.6),
            Barrier(bounds.centerx - 20, bounds.bottom - 92, 40, 12, period=2.8, on_time=1.4),
            Barrier(bounds.centerx - 120, bounds.centery - 6, 50, 12, period=3.5, on_time=1.5),
            Barrier(bounds.centerx + 70, bounds.centery - 6, 50, 12, period=3.0, on_time=1.7),
        ]
        self._sprites = {a.seed: make_asteroid_sprite(a.seed, a.radius) for a in self.asteroids}

    def update_hazards(self, dt: float) -> None:
        b = self.bounds
        for a in self.asteroids:
            a.x += a.vx * dt
            a.y += a.vy * dt
            a.angle += a.spin * dt
            if a.x - a.radius < b.left + 8 or a.x + a.radius > b.right - 8:
                a.vx *= -1
                a.x = max(b.left + 8 + a.radius, min(b.right - 8 - a.radius, a.x))
            if a.y - a.radius < b.top + 8 or a.y + a.radius > b.bottom - 8:
                a.vy *= -1
                a.y = max(b.top + 8 + a.radius, min(b.bottom - 8 - a.radius, a.y))
            # keep out of goal mouths roughly
            if abs(a.y - b.centery) < 90 and (a.x < b.left + 100 or a.x > b.right - 100):
                a.vx *= -1
                a.x += a.vx * dt * 2

        for bar in self.barriers:
            bar.timer += dt
            cycle = bar.timer % bar.period
            bar.active = cycle < bar.on_time

    def collide_hazards(self, entity, is_ball: bool = False) -> bool:
        hit = False
        for a in self.asteroids:
            d = dist(entity.x, entity.y, a.x, a.y)
            min_d = entity.radius + a.radius
            if d < min_d and d > 1e-6:
                nx = (entity.x - a.x) / d
                ny = (entity.y - a.y) / d
                overlap = min_d - d
                entity.x += nx * overlap
                entity.y += ny * overlap
                # bounce
                vn = entity.vx * nx + entity.vy * ny
                if vn < 0:
                    entity.vx -= 1.7 * vn * nx
                    entity.vy -= 1.7 * vn * ny
                # nudge asteroid
                a.vx -= nx * 20
                a.vy -= ny * 20
                hit = True

        for bar in self.barriers:
            if not bar.active:
                continue
            rect = pygame.Rect(bar.x, bar.y, bar.w, bar.h)
            # expand by radius
            expanded = rect.inflate(entity.radius * 2, entity.radius * 2)
            if expanded.collidepoint(entity.x, entity.y):
                # push out via nearest edge
                cx, cy = rect.center
                dx = entity.x - cx
                dy = entity.y - cy
                if abs(dx) / max(rect.w, 1) > abs(dy) / max(rect.h, 1):
                    entity.x = rect.right + entity.radius + 1 if dx > 0 else rect.left - entity.radius - 1
                    entity.vx *= -0.85
                else:
                    entity.y = rect.bottom + entity.radius + 1 if dy > 0 else rect.top - entity.radius - 1
                    entity.vy *= -0.85
                hit = True
        return hit

    def draw_floor(self, surface, t: float) -> None:
        draw_debris_floor(surface, t)

    def draw_hazards(self, surface: pygame.Surface, t: float) -> None:
        frame = int(t * 12)
        for bar in self.barriers:
            spr = make_barrier_sprite(int(bar.w), int(bar.h), frame, active=bar.active)
            surface.blit(spr, spr.get_rect(center=(int(bar.x + bar.w / 2), int(bar.y + bar.h / 2))))

        for a in self.asteroids:
            spr = self._sprites[a.seed]
            rotated = pygame.transform.rotate(spr, a.angle * 57.3)
            rect = rotated.get_rect(center=(int(a.x), int(a.y)))
            surface.blit(rotated, rect)
