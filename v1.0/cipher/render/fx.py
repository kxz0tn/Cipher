"""Particles, trails, impact bursts."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from cipher.constants import PARTICLE_SOFT_CAP, WHITE_GLOW
from cipher.render.palette import with_alpha


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: tuple[int, int, int]
    size: float
    drag: float = 0.98
    gravity: float = 0.0

    @property
    def alive(self) -> bool:
        return self.life > 0


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def clear(self) -> None:
        self.particles.clear()

    def emit(
        self,
        x: float,
        y: float,
        count: int,
        color: tuple[int, int, int],
        speed: float = 120.0,
        life: float = 0.4,
        size: float = 3.0,
        spread: float = math.tau,
        angle: float = 0.0,
        drag: float = 0.96,
    ) -> None:
        for _ in range(count):
            if len(self.particles) >= PARTICLE_SOFT_CAP:
                # recycle oldest
                self.particles.pop(0)
            a = angle + random.uniform(-spread / 2, spread / 2)
            sp = speed * random.uniform(0.4, 1.0)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(a) * sp,
                    vy=math.sin(a) * sp,
                    life=life * random.uniform(0.6, 1.0),
                    max_life=life,
                    color=color,
                    size=size * random.uniform(0.5, 1.2),
                    drag=drag,
                )
            )

    def burst(self, x: float, y: float, color: tuple[int, int, int], power: float = 1.0) -> None:
        self.emit(x, y, int(18 * power), color, speed=180 * power, life=0.45, size=3.5)
        self.emit(x, y, int(8 * power), WHITE_GLOW, speed=100 * power, life=0.25, size=2.0)

    def trail(self, x: float, y: float, color: tuple[int, int, int], vx: float = 0, vy: float = 0) -> None:
        self.emit(
            x,
            y,
            2,
            color,
            speed=40,
            life=0.25,
            size=2.5,
            spread=math.pi,
            angle=math.atan2(-vy, -vx) if (vx or vy) else 0,
        )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vx *= p.drag
            p.vy *= p.drag
            p.vy += p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            t = p.life / max(p.max_life, 1e-6)
            alpha = int(255 * t)
            size = max(1, int(p.size * t + 0.5))
            pygame.draw.circle(
                surface,
                with_alpha(p.color, alpha),
                (int(p.x), int(p.y)),
                size,
            )


class Trail:
    def __init__(self, max_points: int = 12) -> None:
        self.points: list[tuple[float, float, float]] = []  # x, y, age
        self.max_points = max_points

    def add(self, x: float, y: float) -> None:
        self.points.append((x, y, 0.0))
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update(self, dt: float) -> None:
        self.points = [(x, y, a + dt) for x, y, a in self.points if a + dt < 0.25]

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int], width: int = 3) -> None:
        if len(self.points) < 2:
            return
        for i in range(1, len(self.points)):
            x0, y0, a0 = self.points[i - 1]
            x1, y1, a1 = self.points[i]
            t = 1.0 - (a1 / 0.25)
            alpha = int(200 * t)
            w = max(1, int(width * t))
            # soft outer trail for sports TV energy look
            if w > 1:
                pygame.draw.line(
                    surface,
                    with_alpha(color, alpha // 3),
                    (int(x0), int(y0)),
                    (int(x1), int(y1)),
                    w + 2,
                )
            pygame.draw.line(
                surface,
                with_alpha(color, alpha),
                (int(x0), int(y0)),
                (int(x1), int(y1)),
                w,
            )
