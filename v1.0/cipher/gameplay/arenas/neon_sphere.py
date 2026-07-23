"""Neon Sphere — clean glowing grid arena."""
from __future__ import annotations

from cipher.constants import ARENA_NAMES
from cipher.gameplay.arena import Arena, make_base_geometry
from cipher.render.backgrounds import draw_neon_sphere_floor


class NeonSphereArena(Arena):
    def __init__(self) -> None:
        bounds, left, right, ps, es, bs, pups = make_base_geometry()
        super().__init__(
            arena_id="neon_sphere",
            name=ARENA_NAMES["neon_sphere"],
            bounds=bounds,
            left_goal=left,
            right_goal=right,
            player_spawn=ps,
            enemy_spawn=es,
            ball_spawn=bs,
            powerup_spawns=pups,
            gravity_strength=0.0,
        )

    def draw_floor(self, surface, t: float) -> None:
        draw_neon_sphere_floor(surface, t)
