"""Screen shake and impact flash."""
from __future__ import annotations

import random

import pygame

from cipher.core.math_util import clamp, lerp


class CameraFX:
    def __init__(self) -> None:
        self.shake_time = 0.0
        self.shake_duration = 0.0
        self.shake_mag = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.flash_time = 0.0
        self.flash_duration = 0.0
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.chromatic = 0.0

    def shake(self, magnitude: float, duration: float = 0.2) -> None:
        # Keep the stronger of overlapping shakes
        if magnitude >= self.shake_mag * (self.shake_time / max(self.shake_duration, 1e-6)):
            self.shake_mag = magnitude
            self.shake_duration = duration
            self.shake_time = duration

    def flash(self, color: tuple[int, int, int], alpha: int = 120, duration: float = 0.12) -> None:
        self.flash_color = color
        self.flash_alpha = alpha
        self.flash_duration = duration
        self.flash_time = duration

    def impact(self, magnitude: float = 6.0) -> None:
        self.shake(magnitude, 0.18)
        self.flash((255, 255, 255), 90, 0.08)
        self.chromatic = min(1.0, self.chromatic + 0.5)

    def goal_burst(self) -> None:
        self.shake(14.0, 0.45)
        self.flash((0, 240, 255), 160, 0.25)
        self.chromatic = 1.0

    def update(self, dt: float) -> None:
        if self.shake_time > 0:
            self.shake_time = max(0.0, self.shake_time - dt)
            t = self.shake_time / max(self.shake_duration, 1e-6)
            mag = self.shake_mag * t
            self.offset_x = random.uniform(-mag, mag)
            self.offset_y = random.uniform(-mag, mag)
        else:
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.shake_mag = 0.0

        if self.flash_time > 0:
            self.flash_time = max(0.0, self.flash_time - dt)
        self.chromatic = max(0.0, self.chromatic - dt * 3.5)

    def apply_offset(self, surface: pygame.Surface, target: pygame.Surface) -> None:
        ox = int(self.offset_x)
        oy = int(self.offset_y)
        target.fill((0, 0, 0))
        target.blit(surface, (ox, oy))

    def draw_flash(self, surface: pygame.Surface) -> None:
        if self.flash_time <= 0 or self.flash_duration <= 0:
            return
        t = self.flash_time / self.flash_duration
        alpha = int(self.flash_alpha * t)
        if alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.flash_color, clamp(alpha, 0, 255)))
        surface.blit(overlay, (0, 0))
