"""Low-level procedural pixel-art drawing primitives.

Designed for chunky arcade readability: hard outlines, stepped shading,
soft neon glows (pre-baked alpha layers).
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import pygame

from cipher.render.palette import darken, lighten, lerp_color, with_alpha


Color = tuple[int, int, int]
ColorA = tuple[int, int, int, int]


def new_surface(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w, h), pygame.SRCALPHA)


def blit_center(dst: pygame.Surface, src: pygame.Surface, cx: int, cy: int) -> None:
    dst.blit(src, src.get_rect(center=(cx, cy)))


def soft_glow(
    surf: pygame.Surface,
    cx: int,
    cy: int,
    radius: int,
    color: Color,
    layers: int = 5,
    max_alpha: int = 90,
    falloff: float = 0.72,
) -> None:
    """Radial soft glow (outer layers first)."""
    alpha = max_alpha
    r = radius
    for _ in range(layers):
        if r <= 0 or alpha <= 0:
            break
        pygame.draw.circle(surf, with_alpha(color, int(alpha)), (cx, cy), r)
        r = int(r * falloff)
        alpha = int(alpha * 0.55)


def ring_glow(
    surf: pygame.Surface,
    cx: int,
    cy: int,
    radius: int,
    color: Color,
    width: int = 2,
    alpha: int = 120,
) -> None:
    for i in range(3, 0, -1):
        a = max(10, alpha // (i + 1))
        pygame.draw.circle(surf, with_alpha(color, a), (cx, cy), radius + i, max(1, width + i - 1))
    pygame.draw.circle(surf, with_alpha(color, alpha), (cx, cy), radius, width)


def outline_circle(
    surf: pygame.Surface,
    cx: int,
    cy: int,
    r: int,
    fill: ColorA | Color,
    outline: ColorA | Color,
    outline_w: int = 1,
) -> None:
    pygame.draw.circle(surf, fill, (cx, cy), r)
    pygame.draw.circle(surf, outline, (cx, cy), r, outline_w)


def shade_ellipse(
    surf: pygame.Surface,
    rect: pygame.Rect,
    base: Color,
    light: Color,
    shadow: Color,
    outline: Color | None = None,
) -> None:
    """Simple 3-tone shaded ellipse (arcade form)."""
    pygame.draw.ellipse(surf, with_alpha(shadow, 255), rect)
    mid = rect.inflate(-max(2, rect.w // 6), -max(2, rect.h // 6))
    mid.x += 1
    mid.y -= 1
    if mid.w > 2 and mid.h > 2:
        pygame.draw.ellipse(surf, with_alpha(base, 255), mid)
    hi = rect.inflate(-max(4, rect.w // 3), -max(4, rect.h // 3))
    hi.x += 1
    hi.y -= 2
    if hi.w > 2 and hi.h > 2:
        pygame.draw.ellipse(surf, with_alpha(light, 230), hi)
    if outline is not None:
        pygame.draw.ellipse(surf, with_alpha(outline, 255), rect, 1)


def shade_poly(
    surf: pygame.Surface,
    pts: Sequence[tuple[float, float]],
    base: Color,
    light: Color,
    shadow: Color,
    outline: Color,
) -> None:
    if len(pts) < 3:
        return
    pygame.draw.polygon(surf, with_alpha(shadow, 255), pts)
    # inset-ish highlight: average toward centroid and shift up-left
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    mid = [((p[0] + cx) * 0.5 - 0.5, (p[1] + cy) * 0.5 - 0.8) for p in pts]
    pygame.draw.polygon(surf, with_alpha(base, 255), mid)
    hi = [((p[0] + cx) * 0.5 - 1.2, (p[1] + cy) * 0.5 - 1.6) for p in pts]
    # smaller highlight polygon from first half of verts
    if len(hi) >= 3:
        pygame.draw.polygon(surf, with_alpha(light, 200), hi[: max(3, len(hi) // 2 + 1)])
    pygame.draw.polygon(surf, with_alpha(outline, 255), pts, 1)


def draw_pixel_rect(
    surf: pygame.Surface,
    x: int,
    y: int,
    w: int,
    h: int,
    color: ColorA | Color,
) -> None:
    pygame.draw.rect(surf, color, (x, y, w, h))


def bevel_rect(
    surf: pygame.Surface,
    rect: pygame.Rect,
    base: Color,
    light: Color,
    shadow: Color,
    outline: Color,
    radius: int = 0,
) -> None:
    pygame.draw.rect(surf, with_alpha(base, 255), rect, border_radius=radius)
    # top/left highlight
    if rect.h > 2 and rect.w > 2:
        pygame.draw.line(
            surf,
            with_alpha(light, 220),
            (rect.left + 1, rect.top + 1),
            (rect.right - 2, rect.top + 1),
            1,
        )
        pygame.draw.line(
            surf,
            with_alpha(light, 180),
            (rect.left + 1, rect.top + 1),
            (rect.left + 1, rect.bottom - 2),
            1,
        )
        pygame.draw.line(
            surf,
            with_alpha(shadow, 220),
            (rect.left + 1, rect.bottom - 2),
            (rect.right - 2, rect.bottom - 2),
            1,
        )
        pygame.draw.line(
            surf,
            with_alpha(shadow, 180),
            (rect.right - 2, rect.top + 1),
            (rect.right - 2, rect.bottom - 2),
            1,
        )
    pygame.draw.rect(surf, with_alpha(outline, 255), rect, 1, border_radius=radius)


def neon_line(
    surf: pygame.Surface,
    p0: tuple[int, int],
    p1: tuple[int, int],
    color: Color,
    core_w: int = 1,
    glow_w: int = 3,
) -> None:
    pygame.draw.line(surf, with_alpha(color, 50), p0, p1, glow_w + 2)
    pygame.draw.line(surf, with_alpha(color, 120), p0, p1, glow_w)
    pygame.draw.line(surf, with_alpha(lighten(color, 0.5), 255), p0, p1, core_w)


def dither_fill_circle(
    surf: pygame.Surface,
    cx: int,
    cy: int,
    r: int,
    c0: Color,
    c1: Color,
    density: float = 0.35,
) -> None:
    """Cheap dither between two tones inside a circle."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy > r * r:
                continue
            # checker + radial blend
            t = math.sqrt(dx * dx + dy * dy) / max(r, 1)
            use_hi = ((x + y) & 1) == 0 and t < density
            col = c1 if use_hi else lerp_color(c0, c1, 0.25 * (1.0 - t))
            surf.set_at((x, y), with_alpha(col, 255))


def team_palette(team: str) -> dict[str, Color]:
    """Full shading ramp for Vex (cyan) vs foe (magenta/purple)."""
    if team == "vex":
        primary = (0, 240, 255)       # cyan neon
        secondary = (40, 110, 220)    # deep electric blue
        accent = (180, 255, 255)      # ice highlight
        armor = (18, 36, 72)          # dark armor plate
        armor_mid = (32, 58, 110)
        armor_hi = (70, 120, 180)
        trim = (0, 200, 230)
        thruster = (120, 255, 255)
        visor = (220, 255, 255)
        outline = (0, 30, 50)
        glow = (0, 240, 255)
    else:
        primary = (255, 43, 214)      # magenta
        secondary = (155, 70, 220)    # purple
        accent = (255, 180, 240)      # pink highlight
        armor = (48, 12, 48)          # dark purple armor
        armor_mid = (90, 28, 90)
        armor_hi = (150, 60, 140)
        trim = (255, 80, 200)
        thruster = (255, 140, 255)
        visor = (255, 210, 255)
        outline = (40, 0, 40)
        glow = (255, 43, 214)
    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "armor": armor,
        "armor_mid": armor_mid,
        "armor_hi": armor_hi,
        "trim": trim,
        "thruster": thruster,
        "visor": visor,
        "outline": outline,
        "glow": glow,
        "metal": (50, 55, 70),
        "metal_hi": (120, 130, 150),
        "metal_lo": (25, 28, 38),
        "white": (232, 247, 255),
    }
