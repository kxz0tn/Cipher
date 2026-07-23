"""Arena base geometry and hazards."""
from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from cipher.constants import (
    ARENA_MARGIN,
    GOAL_HEIGHT,
    GOAL_INSET,
    GOAL_WIDTH,
    INTERNAL_H,
    INTERNAL_W,
)
from cipher.core.math_util import dist


@dataclass
class Goal:
    side: str  # left | right
    rect: pygame.Rect

    @property
    def center(self) -> tuple[float, float]:
        return self.rect.centerx, self.rect.centery


@dataclass
class Arena:
    arena_id: str
    name: str
    bounds: pygame.Rect
    left_goal: Goal
    right_goal: Goal
    player_spawn: tuple[float, float]
    enemy_spawn: tuple[float, float]
    ball_spawn: tuple[float, float]
    powerup_spawns: list[tuple[float, float]] = field(default_factory=list)
    gravity_strength: float = 0.0
    gravity_center: tuple[float, float] = (INTERNAL_W / 2, INTERNAL_H / 2)

    def apply_forces(self, entities: list, dt: float, gravity_sign: float = 1.0) -> None:
        """Optional arena-wide forces on objects with x,y,vx,vy."""
        if abs(self.gravity_strength) < 1e-6:
            return
        gx, gy = self.gravity_center
        strength = self.gravity_strength * gravity_sign
        for e in entities:
            dx = gx - e.x
            dy = gy - e.y
            d = max(40.0, (dx * dx + dy * dy) ** 0.5)
            e.vx += (dx / d) * strength * dt
            e.vy += (dy / d) * strength * dt

    def update_hazards(self, dt: float) -> None:
        pass

    def collide_hazards(self, entity, is_ball: bool = False) -> bool:
        """Return True if bounced."""
        return False

    def draw_hazards(self, surface: pygame.Surface, t: float) -> None:
        pass

    def draw_floor(self, surface: pygame.Surface, t: float) -> None:
        pass

    def goal_check(self, x: float, y: float, radius: float) -> str | None:
        """Return 'player' if ball entered enemy (right) goal... 
        Player attacks right goal, enemy attacks left goal.
        Scorer: who benefits.
        """
        # Right goal = player scores
        if self.right_goal.rect.collidepoint(x, y) or (
            x + radius >= self.right_goal.rect.left
            and self.right_goal.rect.top <= y <= self.right_goal.rect.bottom
            and x > self.bounds.centerx
        ):
            if self.right_goal.rect.top - 4 <= y <= self.right_goal.rect.bottom + 4:
                if x >= self.right_goal.rect.left - radius * 0.5:
                    return "player"
        # Left goal = enemy scores
        if self.left_goal.rect.collidepoint(x, y) or (
            x - radius <= self.left_goal.rect.right
            and self.left_goal.rect.top <= y <= self.left_goal.rect.bottom
            and x < self.bounds.centerx
        ):
            if self.left_goal.rect.top - 4 <= y <= self.left_goal.rect.bottom + 4:
                if x <= self.left_goal.rect.right + radius * 0.5:
                    return "enemy"
        return None


def make_base_geometry() -> tuple[pygame.Rect, Goal, Goal, tuple, tuple, tuple, list]:
    m = ARENA_MARGIN
    bounds = pygame.Rect(m, m, INTERNAL_W - 2 * m, INTERNAL_H - 2 * m)
    cy = bounds.centery
    gh = GOAL_HEIGHT
    gw = GOAL_WIDTH
    left = Goal(
        "left",
        pygame.Rect(bounds.left - GOAL_INSET, cy - gh // 2, gw, gh),
    )
    right = Goal(
        "right",
        pygame.Rect(bounds.right - gw + GOAL_INSET, cy - gh // 2, gw, gh),
    )
    player_spawn = (bounds.left + 120, cy)
    enemy_spawn = (bounds.right - 120, cy)
    ball_spawn = (bounds.centerx, cy)
    powerup_spawns = [
        (bounds.centerx, cy - 100),
        (bounds.centerx, cy + 100),
        (bounds.centerx - 180, cy),
        (bounds.centerx + 180, cy),
        (bounds.centerx - 100, cy - 80),
        (bounds.centerx + 100, cy + 80),
    ]
    return bounds, left, right, player_spawn, enemy_spawn, ball_spawn, powerup_spawns


def create_arena(arena_id: str) -> Arena:
    if arena_id == "debris_field":
        from cipher.gameplay.arenas.debris_field import DebrisFieldArena

        return DebrisFieldArena()
    if arena_id == "gravity_well":
        from cipher.gameplay.arenas.gravity_well import GravityWellArena

        return GravityWellArena()
    from cipher.gameplay.arenas.neon_sphere import NeonSphereArena

    return NeonSphereArena()
