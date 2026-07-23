"""Sprite factory: baked Imagine pixel-art assets + procedural fallbacks.

Prefer high-quality generated PNGs in cipher/assets/. If missing, fall back
to procedural pixel construction so the game always runs.
"""
from __future__ import annotations

import math
import random
from functools import lru_cache

import pygame

from cipher.constants import BALL_RADIUS, POWERUP_RADIUS, WHITE_GLOW, YELLOW
from cipher.render.assets import has_baked_assets, load_image
from cipher.render.palette import POWERUP_COLORS, darken, lighten, with_alpha
from cipher.render.pixel import (
    bevel_rect,
    neon_line,
    new_surface,
    ring_glow,
    shade_ellipse,
    shade_poly,
    soft_glow,
    team_palette,
)

# Display sizes (visual; collision radii stay in gameplay constants)
# Large arcade-sports readable athletes (Jam/Blitz spirit)
CHAR_DRAW_SIZE = 84
BALL_DRAW_SIZE = 46
POWER_DRAW_SIZE = 44


def _scale(surf: pygame.Surface, size: int) -> pygame.Surface:
    if surf.get_width() == size and surf.get_height() == size:
        return surf
    return pygame.transform.smoothscale(surf, (size, size))


def _scale_box(surf: pygame.Surface, w: int, h: int) -> pygame.Surface:
    if surf.get_width() == w and surf.get_height() == h:
        return surf
    return pygame.transform.smoothscale(surf, (w, h))


# ---------------------------------------------------------------------------
# Baked asset paths
# ---------------------------------------------------------------------------

_PLAYER_FILES = {
    ("vex", "idle"): "vex_idle.png",
    ("vex", "move"): None,  # multi-frame
    ("vex", "dash"): "vex_dash.png",
    ("foe", "idle"): "foe_idle.png",
    ("foe", "move"): None,
    ("foe", "dash"): "foe_dash.png",
}


@lru_cache(maxsize=128)
def make_player_sprite(
    team: str = "vex",
    frame: int = 0,
    anim: str = "idle",
) -> pygame.Surface:
    if anim not in ("idle", "move", "dash"):
        anim = "idle"
    frame = int(frame) % 8
    team = "vex" if team == "vex" else "foe"

    if has_baked_assets():
        surf = _load_player_baked(team, anim, frame)
        if surf is not None:
            return surf

    return _make_player_procedural(team, frame, anim)


def _load_player_baked(team: str, anim: str, frame: int) -> pygame.Surface | None:
    if anim == "move":
        name = f"{team}_move_{frame % 4}.png"
        img = load_image(name)
        if img is None:
            img = load_image(f"{team}_idle.png")
    elif anim == "dash":
        img = load_image(f"{team}_dash.png") or load_image(f"{team}_idle.png")
    else:
        # idle subtle alternate
        if team == "vex" and (frame % 4) >= 2:
            img = load_image("vex_idle_b.png") or load_image("vex_idle.png")
        else:
            img = load_image(f"{team}_idle.png")
    if img is None:
        return None
    return _scale(img, CHAR_DRAW_SIZE)


@lru_cache(maxsize=32)
def make_ball_sprite(frame: int = 0) -> pygame.Surface:
    frame = int(frame) % 16
    if has_baked_assets():
        # pulse between base and alt / frame variants
        if frame % 8 >= 4:
            img = load_image("ball_pulse.png") or load_image(f"ball_f{frame % 4}.png")
        else:
            img = load_image(f"ball_f{frame % 4}.png") or load_image("ball.png")
        if img is not None:
            # subtle scale pulse
            pulse = 1.0 + 0.06 * math.sin(frame * 0.5)
            size = max(24, int(BALL_DRAW_SIZE * pulse))
            return _scale(img, size)

    return _make_ball_procedural(frame)


@lru_cache(maxsize=64)
def make_powerup_sprite(kind: str, frame: int = 0) -> pygame.Surface:
    frame = int(frame) % 16
    if has_baked_assets():
        name = {
            "speed": "power_speed.png",
            "multiball": "power_multiball.png",
            "gravity": "power_gravity.png",
            "shield": "power_shield.png",
            "overdrive": "power_overdrive.png",
        }.get(kind)
        if name:
            img = load_image(name)
            if img is not None:
                pulse = 1.0 + 0.08 * math.sin(frame * 0.4)
                size = max(28, int(POWER_DRAW_SIZE * pulse))
                base = _scale(img, size)
                # soft team glow ring
                canvas = new_surface(size + 16, size + 16)
                color = POWERUP_COLORS.get(kind, YELLOW)
                soft_glow(canvas, (size + 16) // 2, (size + 16) // 2, size // 2 + 4, color, 3, 55)
                canvas.blit(base, (8, 8))
                return canvas

    return _make_powerup_procedural(kind, frame)


@lru_cache(maxsize=8)
def make_goal_surface(height: int, side: str, frame: int = 0) -> pygame.Surface:
    if has_baked_assets():
        name = "goal_left.png" if side == "left" else "goal_right.png"
        img = load_image(name)
        if img is not None:
            # Tall sports goals — preserve aspect, keep readable
            target_h = max(height + 48, 210)
            aspect = img.get_width() / max(img.get_height(), 1)
            target_w = max(64, min(110, int(target_h * aspect)))
            return _scale_box(img, target_w, target_h)

    return _make_goal_procedural(height, side, frame)


@lru_cache(maxsize=16)
def make_asteroid_sprite(seed: int = 0, radius: int = 20) -> pygame.Surface:
    return _make_asteroid_procedural(seed, radius)


@lru_cache(maxsize=16)
def make_barrier_sprite(
    width: int = 50, height: int = 12, frame: int = 0, active: bool = True
) -> pygame.Surface:
    return _make_barrier_procedural(width, height, frame, active)


def clear_sprite_cache() -> None:
    make_player_sprite.cache_clear()
    make_ball_sprite.cache_clear()
    make_powerup_sprite.cache_clear()
    make_asteroid_sprite.cache_clear()
    make_goal_surface.cache_clear()
    make_barrier_sprite.cache_clear()
    from cipher.render.assets import clear_asset_cache

    clear_asset_cache()


# ---------------------------------------------------------------------------
# Procedural fallbacks (kept for resilience)
# ---------------------------------------------------------------------------

CHAR_W = 56
CHAR_H = 64


def _thruster_plume(surf, cx, y, pal, length, width, frame, intense=False):
    flicker = frame % 4
    length = length + flicker
    if intense:
        length = int(length * 1.55)
        width = width + 2
    for i in range(4, 0, -1):
        alpha = 30 + i * 22
        w = width + i * 2
        h = length + i
        rect = pygame.Rect(0, 0, w, h)
        rect.midtop = (cx, y - 1)
        pygame.draw.ellipse(surf, with_alpha(pal["glow"], alpha // 2), rect)
    colors = (
        with_alpha(pal["glow"], 70),
        with_alpha(pal["thruster"], 160),
        with_alpha(pal["accent"], 220),
        with_alpha(pal["white"], 255),
    )
    scales = (1.0, 0.72, 0.45, 0.22)
    for col, sc in zip(colors, scales):
        w = max(2, int(width * sc))
        h = max(3, int(length * sc))
        rect = pygame.Rect(0, 0, w, h)
        rect.midtop = (cx + (1 if flicker == 1 else -1 if flicker == 3 else 0), y)
        pygame.draw.ellipse(surf, col, rect)


def _make_player_procedural(team: str, frame: int, anim: str) -> pygame.Surface:
    pal = team_palette(team)
    surf = new_surface(CHAR_W, CHAR_H)
    cx, cy = CHAR_W // 2, CHAR_H // 2 + 2
    bob = 0 if anim != "idle" or (frame % 4) < 2 else -1
    if anim == "dash":
        bob = 1
    body_y = cy + bob
    soft_glow(surf, cx, body_y + 2, 22, pal["glow"], 4, 55)
    thruster_len = 10 if anim == "idle" else 14 if anim == "move" else 22
    _thruster_plume(surf, cx - 6, body_y + 16, pal, thruster_len, 6, frame, anim == "dash")
    _thruster_plume(surf, cx + 6, body_y + 16, pal, thruster_len, 6, frame, anim == "dash")
    shade_ellipse(
        surf,
        pygame.Rect(cx - 11, body_y - 12, 22, 28),
        pal["armor_mid"],
        pal["armor_hi"],
        pal["armor"],
        pal["outline"],
    )
    # head
    shade_ellipse(
        surf,
        pygame.Rect(cx - 8, body_y - 20, 16, 14),
        pal["armor_mid"],
        pal["armor_hi"],
        pal["armor"],
        pal["outline"],
    )
    pygame.draw.rect(surf, with_alpha(pal["visor"], 255), (cx - 6, body_y - 15, 12, 4), border_radius=1)
    soft_glow(surf, cx, body_y - 13, 7, pal["glow"], 2, 70)
    pygame.draw.circle(surf, with_alpha(pal["primary"], 255), (cx, body_y - 2), 3)
    return _scale(surf, CHAR_DRAW_SIZE)


def _make_ball_procedural(frame: int) -> pygame.Surface:
    r = BALL_RADIUS
    size = r * 2 + 36
    surf = new_surface(size, size)
    cx = cy = size // 2
    pulse = 1.0 + 0.12 * math.sin(frame * 0.45)
    soft_glow(surf, cx, cy, int((r + 14) * pulse), (0, 240, 255), 5, 70)
    soft_glow(surf, cx, cy, int((r + 8) * pulse), (255, 43, 214), 3, 40)
    pygame.draw.circle(surf, with_alpha((0, 200, 255), 220), (cx, cy), int(r * pulse) + 2)
    pygame.draw.circle(surf, with_alpha((200, 255, 255), 255), (cx, cy), max(3, r - 4))
    pygame.draw.circle(surf, with_alpha((255, 255, 255), 255), (cx - 1, cy - 2), 3)
    pygame.draw.circle(surf, with_alpha((255, 43, 214), 200), (cx, cy), r - 1, 1)
    return surf


def _make_powerup_procedural(kind: str, frame: int) -> pygame.Surface:
    color = POWERUP_COLORS.get(kind, YELLOW)
    r = POWERUP_RADIUS + 2
    size = r * 2 + 28
    surf = new_surface(size, size)
    cx = cy = size // 2
    pulse = 1.0 + 0.08 * math.sin(frame * 0.4)
    soft_glow(surf, cx, cy, int((r + 10) * pulse), color, 4, 75)
    pygame.draw.circle(surf, with_alpha(darken(color, 0.35), 255), (cx, cy), int(r * pulse))
    pygame.draw.circle(surf, with_alpha(color, 230), (cx, cy), int(r * pulse) - 3)
    pygame.draw.circle(surf, with_alpha(WHITE_GLOW, 200), (cx - 2, cy - 3), 2)
    return surf


def _make_goal_procedural(height: int, side: str, frame: int = 0) -> pygame.Surface:
    frame = int(frame) % 12
    w = 48
    h = height + 28
    surf = new_surface(w, h)
    color = (0, 240, 255) if side == "left" else (255, 43, 214)
    accent = (180, 255, 255) if side == "left" else (255, 180, 240)
    dark = darken(color, 0.25)
    pulse = 0.55 + 0.45 * abs(math.sin(frame * 0.35))
    pygame.draw.rect(surf, with_alpha(color, int(40 + 30 * pulse)), (2, 4, w - 4, h - 8), border_radius=6)
    plate = pygame.Rect(8, 10, w - 16, h - 20)
    pygame.draw.rect(surf, with_alpha((10, 4, 20), 220), plate, border_radius=3)
    for post in (pygame.Rect(4, 6, 7, h - 12), pygame.Rect(w - 11, 6, 7, h - 12)):
        bevel_rect(surf, post, dark, color, darken(dark, 0.7), accent, 2)
    return surf


def _make_asteroid_procedural(seed: int, radius: int) -> pygame.Surface:
    rng = random.Random(seed * 97 + radius)
    pad = 14
    size = radius * 2 + pad * 2
    surf = new_surface(size, size)
    cx = cy = size // 2
    n = rng.randint(7, 10)
    pts = []
    for i in range(n):
        ang = (i / n) * math.tau + rng.uniform(-0.12, 0.12)
        rr = radius * rng.uniform(0.72, 1.05)
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    soft_glow(surf, cx, cy, radius + 6, (155, 92, 255), 3, 35)
    pygame.draw.polygon(surf, with_alpha((48, 32, 62), 255), pts)
    pygame.draw.polygon(surf, with_alpha((255, 120, 220), 160), pts, 2)
    return surf


def _make_barrier_procedural(width: int, height: int, frame: int, active: bool) -> pygame.Surface:
    frame = int(frame) % 8
    pad = 8
    surf = new_surface(width + pad * 2, height + pad * 2)
    if not active:
        pygame.draw.rect(surf, with_alpha((255, 220, 60), 40), (pad, pad, width, height), 1, border_radius=2)
        return surf
    color = (255, 220, 60)
    soft_glow(surf, pad + width // 2, pad + height // 2, max(width, height), color, 3, 50)
    body = pygame.Rect(pad, pad, width, height)
    pygame.draw.rect(surf, with_alpha(darken(color, 0.35), 230), body, border_radius=3)
    for i, x in enumerate(range(body.left + 2, body.right - 2, 4)):
        phase = (frame + i) % 4
        pygame.draw.line(
            surf,
            with_alpha((255, 120, 60) if phase > 1 else color, 80 + phase * 40),
            (x, body.top + 2),
            (x, body.bottom - 2),
            2,
        )
    pygame.draw.rect(surf, with_alpha((255, 80, 160), 230), body, 2, border_radius=3)
    return surf
