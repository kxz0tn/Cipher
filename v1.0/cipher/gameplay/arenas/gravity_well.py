"""Gravity Well — central pull and orbiting energy rings."""
from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from cipher.constants import ARENA_NAMES, CYAN, MAGENTA, PURPLE, WHITE_GLOW
from cipher.core.math_util import dist
from cipher.gameplay.arena import Arena, make_base_geometry
from cipher.render.backgrounds import draw_gravity_floor
from cipher.render.palette import lighten, with_alpha


def lighten_col(col: tuple[int, int, int]) -> tuple[int, int, int]:
    return lighten(col, 0.45)


@dataclass
class EnergyRing:
    radius: float
    width: float
    angle: float
    speed: float
    gap: float  # radians of safe gap
    dangerous: bool = True


class GravityWellArena(Arena):
    def __init__(self) -> None:
        bounds, left, right, ps, es, bs, pups = make_base_geometry()
        super().__init__(
            arena_id="gravity_well",
            name=ARENA_NAMES["gravity_well"],
            bounds=bounds,
            left_goal=left,
            right_goal=right,
            player_spawn=ps,
            enemy_spawn=es,
            ball_spawn=bs,
            powerup_spawns=pups,
            gravity_strength=140.0,
            gravity_center=(bounds.centerx, bounds.centery),
        )
        self.rings = [
            EnergyRing(radius=90, width=10, angle=0.0, speed=0.9, gap=1.2),
            EnergyRing(radius=150, width=10, angle=1.0, speed=-0.65, gap=1.0),
            EnergyRing(radius=210, width=8, angle=2.0, speed=0.45, gap=0.9),
        ]

    def update_hazards(self, dt: float) -> None:
        for ring in self.rings:
            ring.angle += ring.speed * dt

    def collide_hazards(self, entity, is_ball: bool = False) -> bool:
        hit = False
        cx, cy = self.gravity_center
        for ring in self.rings:
            d = dist(entity.x, entity.y, cx, cy)
            band = abs(d - ring.radius)
            if band > ring.width + entity.radius:
                continue
            # angle of entity
            ang = math.atan2(entity.y - cy, entity.x - cx)
            # normalize relative to ring angle
            rel = (ang - ring.angle + math.pi) % math.tau - math.pi
            # gap centered at ring.angle
            if abs(rel) < ring.gap * 0.5:
                continue  # safe sector
            # bounce outward/inward
            nx = (entity.x - cx) / max(d, 1e-6)
            ny = (entity.y - cy) / max(d, 1e-6)
            # push to nearest edge of band
            if d >= ring.radius:
                target = ring.radius + ring.width + entity.radius
            else:
                target = ring.radius - ring.width - entity.radius
            entity.x = cx + nx * target
            entity.y = cy + ny * target
            vn = entity.vx * nx + entity.vy * ny
            # if moving into ring, reflect
            if (d < ring.radius and vn > 0) or (d >= ring.radius and vn < 0):
                entity.vx -= 1.6 * vn * nx
                entity.vy -= 1.6 * vn * ny
            else:
                entity.vx += nx * 40
                entity.vy += ny * 40
            hit = True
        return hit

    def draw_floor(self, surface, t: float) -> None:
        draw_gravity_floor(surface, t)

    def draw_hazards(self, surface: pygame.Surface, t: float) -> None:
        cx, cy = int(self.gravity_center[0]), int(self.gravity_center[1])
        pulse = 0.6 + 0.4 * abs(math.sin(t * 3.0))
        # central well core
        for r, a in ((28, 30), (18, 60), (10, 120), (4, 220)):
            pygame.draw.circle(surface, with_alpha(MAGENTA, int(a * pulse)), (cx, cy), r)
        pygame.draw.circle(surface, with_alpha(WHITE_GLOW, 230), (cx, cy), 3)

        for i, ring in enumerate(self.rings):
            col = (PURPLE, MAGENTA, CYAN)[i % 3]
            hi = lighten_col(col)
            segs = 64
            for s in range(segs):
                a0 = ring.angle + (s / segs) * math.tau
                a1 = ring.angle + ((s + 1) / segs) * math.tau
                mid = (a0 + a1) * 0.5
                rel = (mid - ring.angle + math.pi) % math.tau - math.pi
                if abs(rel) < ring.gap * 0.5:
                    continue
                x0 = cx + math.cos(a0) * ring.radius
                y0 = cy + math.sin(a0) * ring.radius
                x1 = cx + math.cos(a1) * ring.radius
                y1 = cy + math.sin(a1) * ring.radius
                # glow underlay + hot core
                pygame.draw.line(surface, with_alpha(col, 50), (x0, y0), (x1, y1), int(ring.width) + 4)
                pygame.draw.line(surface, with_alpha(col, 180), (x0, y0), (x1, y1), int(ring.width))
                pygame.draw.line(surface, with_alpha(hi, 220), (x0, y0), (x1, y1), max(1, int(ring.width) - 3))
            # gap portal markers
            for sign in (-1, 1):
                ga = ring.angle + sign * ring.gap * 0.5
                gx = cx + math.cos(ga) * ring.radius
                gy = cy + math.sin(ga) * ring.radius
                pygame.draw.circle(surface, with_alpha(col, 100), (int(gx), int(gy)), 6)
                pygame.draw.circle(surface, with_alpha(WHITE_GLOW, 230), (int(gx), int(gy)), 3)
                pygame.draw.circle(surface, with_alpha(hi, 255), (int(gx), int(gy)), 1)
