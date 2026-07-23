"""Cyberpunk glitch text effect for the CIPHER title wordmark."""
from __future__ import annotations

import math
import random

import pygame

from cipher.constants import CYAN, MAGENTA, WHITE_GLOW
from cipher.render.font import get_font
from cipher.render.palette import with_alpha


def draw_glitch_text(
    surface: pygame.Surface,
    text: str,
    center: tuple[int, int],
    size: int,
    t: float,
) -> pygame.Rect:
    """Draw text with RGB channel split, scan tears, and intermittent glitch frames."""
    font = get_font(size, bold=True, title=True)
    # Phase-driven glitch intensity
    beat = abs(math.sin(t * 3.1))
    hard = (int(t * 7) % 17) in (0, 1, 8)  # occasional heavy glitch
    intensity = 0.35 + 0.65 * beat
    if hard:
        intensity = 1.0

    # Base colors
    col_main = WHITE_GLOW
    col_a = CYAN
    col_b = MAGENTA

    base = font.render(text, True, col_main)
    layer_a = font.render(text, True, col_a)
    layer_b = font.render(text, True, col_b)

    # Outline
    black = font.render(text, True, (0, 0, 0))
    ow = 3
    pad = ow + 12
    w = base.get_width() + pad * 2
    h = base.get_height() + pad * 2
    canvas = pygame.Surface((w, h), pygame.SRCALPHA)

    ox = pad
    oy = pad

    # Black outline
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx == 0 and dy == 0:
                continue
            canvas.blit(black, (ox + dx, oy + dy))

    # Chromatic aberration offsets
    split = int(2 + intensity * 5)
    if hard:
        split = int(6 + random.random() * 4)
    canvas.blit(layer_a, (ox - split, oy), special_flags=pygame.BLEND_RGBA_ADD)
    canvas.blit(layer_b, (ox + split, oy + (1 if hard else 0)), special_flags=pygame.BLEND_RGBA_ADD)
    canvas.blit(base, (ox, oy))

    # Horizontal tear slices
    n_slices = 3 if hard else 1
    if intensity > 0.5 or hard:
        for _ in range(n_slices):
            sy = random.randint(0, max(1, h - 6))
            sh = random.randint(2, 6)
            shift = random.randint(-10, 10) if hard else random.randint(-4, 4)
            band = canvas.subsurface((0, sy, w, min(sh, h - sy))).copy()
            canvas.fill((0, 0, 0, 0), (0, sy, w, min(sh, h - sy)))
            canvas.blit(band, (shift, sy))

    # Scanline overlay
    for y in range(0, h, 3):
        pygame.draw.line(canvas, with_alpha((0, 0, 0), 40), (0, y), (w, y), 1)

    # Occasional bright flash bar
    if hard:
        fy = random.randint(0, max(1, h - 4))
        pygame.draw.rect(canvas, with_alpha(CYAN, 90), (0, fy, w, 3))

    rect = canvas.get_rect(center=center)
    surface.blit(canvas, rect)
    return rect
