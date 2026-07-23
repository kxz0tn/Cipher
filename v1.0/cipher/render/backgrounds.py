"""Dark cyberpunk sports arena + premium title/menu presentation."""
from __future__ import annotations

import math
import random

import pygame

from cipher.constants import (
    ARENA_MARGIN,
    BG_DEEP,
    CYAN,
    ELEC_BLUE,
    HOT_PINK,
    INTERNAL_H,
    INTERNAL_W,
    MAGENTA,
    PURPLE,
    WHITE_GLOW,
    YELLOW,
)
from cipher.render.assets import load_image
from cipher.render.palette import darken, lighten, with_alpha


class Starfield:
    def __init__(self, seed: int = 42) -> None:
        rng = random.Random(seed)
        self.stars: list[tuple[float, float, float, int, tuple[int, int, int]]] = []
        for _ in range(260):
            col = rng.choice(
                (WHITE_GLOW, (160, 140, 220), (80, 200, 220), (180, 80, 200), (120, 120, 160))
            )
            self.stars.append(
                (
                    rng.uniform(0, INTERNAL_W),
                    rng.uniform(0, INTERNAL_H),
                    rng.uniform(0.06, 1.2),
                    rng.randint(1, 2),
                    col,
                )
            )
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        for i, (x, y, speed, size, col) in enumerate(self.stars):
            x += speed * 6 * dt
            if x > INTERNAL_W:
                x = 0.0
                y = (y + 67) % INTERNAL_H
            self.stars[i] = (x, y, speed, size, col)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((3, 2, 8))  # near-black, not pink
        for i, col in enumerate(((60, 20, 80), (20, 40, 70), (40, 10, 50))):
            cx = int(INTERNAL_W * (0.2 + i * 0.28) + math.sin(self.t * 0.08 + i) * 20)
            cy = int(INTERNAL_H * (0.3 + (i % 2) * 0.2))
            blob = pygame.Surface((300, 180), pygame.SRCALPHA)
            pygame.draw.ellipse(blob, with_alpha(col, 22), (0, 0, 300, 180))
            surface.blit(blob, (cx - 150, cy - 90))
        for x, y, speed, size, col in self.stars:
            tw = 0.7 + 0.3 * math.sin(self.t * 1.8 + x * 0.02)
            pygame.draw.circle(
                surface,
                with_alpha(col, int((90 + speed * 70) * tw)),
                (int(x), int(y)),
                size,
            )


def draw_arena_frame(surface: pygame.Surface, color: tuple[int, int, int] = CYAN) -> pygame.Rect:
    m = ARENA_MARGIN
    rect = pygame.Rect(m, m, INTERNAL_W - 2 * m, INTERNAL_H - 2 * m)

    outer = rect.inflate(24, 24)
    pygame.draw.rect(surface, with_alpha((8, 6, 18), 255), outer, border_radius=14)
    pygame.draw.rect(surface, with_alpha(darken(color, 0.25), 255), outer, 3, border_radius=14)

    for i in range(4, 0, -1):
        r = rect.inflate(i * 4, i * 4)
        pygame.draw.rect(surface, with_alpha(color, 18 + i * 20), r, 2, border_radius=10)

    pygame.draw.rect(surface, with_alpha(color, 255), rect, 3, border_radius=8)
    pygame.draw.rect(surface, with_alpha(lighten(color, 0.4), 160), rect.inflate(-4, -4), 1, border_radius=6)

    for (x, y) in (
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom),
    ):
        pygame.draw.rect(surface, with_alpha((12, 8, 28), 255), (x - 10, y - 10, 20, 20), border_radius=2)
        pygame.draw.rect(surface, with_alpha(color, 255), (x - 10, y - 10, 20, 20), 2, border_radius=2)
        pygame.draw.circle(surface, with_alpha(YELLOW, 240), (x, y), 4)
    return rect


def _draw_boards(surface: pygame.Surface, rect: pygame.Rect) -> None:
    boards = load_image("arena_boards.png")
    if boards is None:
        # Procedural LED strip
        for y in (rect.y - 18, rect.bottom):
            strip = pygame.Rect(rect.x, y, rect.w, 16)
            pygame.draw.rect(surface, with_alpha((10, 8, 24), 255), strip)
            for x in range(rect.x + 8, rect.right - 8, 28):
                c = CYAN if ((x // 28) % 2 == 0) else MAGENTA
                pygame.draw.rect(surface, with_alpha(c, 160), (x, y + 3, 18, 10), border_radius=2)
        return
    top = pygame.transform.smoothscale(boards, (rect.w, 20))
    bot = pygame.transform.flip(top, False, True)
    surface.blit(top, (rect.x, rect.y - 18))
    surface.blit(bot, (rect.x, rect.bottom - 2))


def _blit_pitch(floor: pygame.Surface, theme: str, t: float) -> None:
    w, h = floor.get_size()
    pitch = load_image("arena_pitch.png")
    detail = load_image("pitch_detail.png")

    if pitch is not None:
        floor.blit(pygame.transform.smoothscale(pitch, (w, h)), (0, 0))
    else:
        floor.fill(with_alpha((10, 16, 32), 255))

    # Detail circuit overlay for depth (not empty)
    if detail is not None:
        tile = pygame.transform.smoothscale(detail, (128, 128))
        tile.set_alpha(35 if theme == "neon" else 28)
        for y in range(0, h, 128):
            for x in range(0, w, 128):
                floor.blit(tile, (x, y))

    if theme == "debris":
        wash = pygame.Surface((w, h), pygame.SRCALPHA)
        wash.fill(with_alpha(HOT_PINK, 22))
        floor.blit(wash, (0, 0))
        for i in range(-h, w, 64):
            pygame.draw.line(floor, with_alpha(HOT_PINK, 18), (i, 0), (i + h, h), 10)
    elif theme == "gravity":
        wash = pygame.Surface((w, h), pygame.SRCALPHA)
        wash.fill(with_alpha(PURPLE, 30))
        floor.blit(wash, (0, 0))
        cx, cy = w // 2, h // 2
        for i in range(7, 0, -1):
            pygame.draw.circle(floor, with_alpha(PURPLE, 12 + i * 7), (cx, cy), 20 + i * 30, 2)
        for k in range(8):
            ang = t * 0.45 + k * math.tau / 8
            pygame.draw.line(
                floor,
                with_alpha(ELEC_BLUE, 36),
                (cx, cy),
                (cx + int(math.cos(ang) * 200), cy + int(math.sin(ang) * 200)),
                1,
            )

    # Energy border life
    pulse = 100 + int(80 * abs(math.sin(t * 2.5)))
    pygame.draw.rect(floor, with_alpha(CYAN, pulse // 2), (1, 1, w - 2, 3))
    pygame.draw.rect(floor, with_alpha(MAGENTA, pulse // 2), (1, h - 4, w - 2, 3))
    pygame.draw.rect(floor, with_alpha(CYAN, pulse // 3), (1, 1, 3, h - 2))
    pygame.draw.rect(floor, with_alpha(MAGENTA, pulse // 3), (w - 4, 1, 3, h - 2))

    # Holo scanline
    scan_y = int((t * 55) % max(h - 8, 1)) + 4
    pygame.draw.line(floor, with_alpha(WHITE_GLOW, 22), (10, scan_y), (w - 10, scan_y), 1)

    # Floating data nodes (visual interest)
    for i in range(6):
        nx = int(w * (0.15 + i * 0.14) + math.sin(t + i) * 8)
        ny = int(h * (0.25 + (i % 3) * 0.22) + math.cos(t * 0.7 + i) * 6)
        pygame.draw.circle(floor, with_alpha(CYAN if i % 2 == 0 else MAGENTA, 50), (nx, ny), 3)
        pygame.draw.circle(floor, with_alpha(WHITE_GLOW, 80), (nx, ny), 1)

    # Center pulse
    if theme == "neon":
        p = 45 + int(40 * abs(math.sin(t * 1.5)))
        pygame.draw.circle(floor, with_alpha(CYAN, p), (w // 2, h // 2), 68, 2)
        pygame.draw.circle(floor, with_alpha(WHITE_GLOW, p // 2), (w // 2, h // 2), 8, 1)

    # Soft top vignette only (keep field dark, not washed)
    vig = pygame.Surface((w, h // 6), pygame.SRCALPHA)
    for y in range(h // 6):
        vig.fill(with_alpha((0, 0, 0), int(20 * (1 - y / max(h // 6, 1)))), (0, y, w, 1))
    floor.blit(vig, (0, 0))


def draw_neon_sphere_floor(surface: pygame.Surface, t: float) -> None:
    m = ARENA_MARGIN
    rect = pygame.Rect(m, m, INTERNAL_W - 2 * m, INTERNAL_H - 2 * m)
    floor = pygame.Surface(rect.size, pygame.SRCALPHA)
    _blit_pitch(floor, "neon", t)
    surface.blit(floor, rect.topleft)
    _draw_boards(surface, rect)
    draw_arena_frame(surface, CYAN)


def draw_debris_floor(surface: pygame.Surface, t: float) -> None:
    m = ARENA_MARGIN
    rect = pygame.Rect(m, m, INTERNAL_W - 2 * m, INTERNAL_H - 2 * m)
    floor = pygame.Surface(rect.size, pygame.SRCALPHA)
    _blit_pitch(floor, "debris", t)
    surface.blit(floor, rect.topleft)
    _draw_boards(surface, rect)
    draw_arena_frame(surface, HOT_PINK)


def draw_gravity_floor(surface: pygame.Surface, t: float) -> None:
    m = ARENA_MARGIN
    rect = pygame.Rect(m, m, INTERNAL_W - 2 * m, INTERNAL_H - 2 * m)
    floor = pygame.Surface(rect.size, pygame.SRCALPHA)
    _blit_pitch(floor, "gravity", t)
    surface.blit(floor, rect.topleft)
    _draw_boards(surface, rect)
    draw_arena_frame(surface, PURPLE)


def draw_menu_background(surface: pygame.Surface, starfield: Starfield, t: float) -> None:
    """Dark hangar / cyber UI backdrop — never flat pink."""
    menu_bg = load_image("menu_bg.png")
    if menu_bg is not None:
        surface.blit(pygame.transform.smoothscale(menu_bg, (INTERNAL_W, INTERNAL_H)), (0, 0))
        dim = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
        dim.fill(with_alpha((2, 1, 8), 130))
        surface.blit(dim, (0, 0))
    else:
        starfield.draw(surface)

    # Thin neon edge frame only
    pygame.draw.rect(surface, with_alpha(CYAN, 35), (0, 0, INTERNAL_W, 3))
    pygame.draw.rect(surface, with_alpha(MAGENTA, 30), (0, INTERNAL_H - 3, INTERNAL_W, 3))


def draw_title_background(surface: pygame.Surface, t: float) -> None:
    """Dark premium title — pure dark cyberpunk, no pink flat fill."""
    title_bg = load_image("title_bg.png")
    if title_bg is not None:
        surface.blit(pygame.transform.smoothscale(title_bg, (INTERNAL_W, INTERNAL_H)), (0, 0))
        # Heavy dark vignette
        vig = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
        for i in range(12):
            pygame.draw.rect(
                vig,
                with_alpha((0, 0, 0), 14 + i * 9),
                vig.get_rect().inflate(-i * 36, -i * 24),
                52,
            )
        surface.blit(vig, (0, 0))
        # Very subtle cool pulse (not magenta flood)
        pulse = int(4 + 4 * abs(math.sin(t * 0.5)))
        wash = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
        wash.fill(with_alpha((20, 10, 40), pulse))
        surface.blit(wash, (0, 0))
    else:
        # Fallback: pure dark starfield — never solid pink
        surface.fill((4, 2, 10))
        starfield = Starfield(1)
        starfield.t = t
        starfield.draw(surface)
