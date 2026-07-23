"""Cyberpunk-readable game typography.

Uses monospaced / geometric tech fonts when available (Cascadia, Consolas,
Bahnschrift), with clean antialiasing and neon-friendly outlines.
"""
from __future__ import annotations

import os
from pathlib import Path

import pygame

from cipher.constants import WHITE_GLOW

# Cyber / tech first, then clean UI fallbacks
_TITLE_CANDIDATES = (
    "Cascadia Mono",
    "Cascadia Code",
    "Consolas",
    "Bahnschrift",
    "Lucida Console",
    "Segoe UI Black",
    "Arial Black",
    "Trebuchet MS",
    "Arial",
)
_BODY_CANDIDATES = (
    "Cascadia Mono",
    "Cascadia Code",
    "Consolas",
    "Bahnschrift",
    "Segoe UI",
    "Lucida Console",
    "Trebuchet MS",
    "Arial",
    "Tahoma",
)

# Windows font file fallbacks (path relative to WINDIR)
_FILE_FALLBACKS = (
    "Fonts/cascadiamono.ttf",
    "Fonts/CascadiaMono.ttf",
    "Fonts/consola.ttf",
    "Fonts/consolab.ttf",
    "Fonts/bahnschrift.ttf",
    "Fonts/lucon.ttf",
    "Fonts/segoeuib.ttf",
    "Fonts/segoeui.ttf",
    "Fonts/arialbd.ttf",
    "Fonts/arial.ttf",
)

_font_cache: dict[tuple[str, int, bool], pygame.font.Font] = {}
_resolved: dict[str, str | None] = {"title": None, "body": None, "file": None}


def _find_sysfont(candidates: tuple[str, ...]) -> str | None:
    if not pygame.font.get_init():
        pygame.font.init()
    available = {n.lower().replace(" ", "") for n in pygame.font.get_fonts()}
    for name in candidates:
        key = name.replace(" ", "").lower()
        if key in available:
            return name
        for a in available:
            if key in a or a in key:
                return name
    return None


def _find_font_file() -> str | None:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    for rel in _FILE_FALLBACKS:
        path = Path(windir) / rel
        if path.is_file():
            return str(path)
    return None


def _resolve() -> None:
    if not pygame.font.get_init():
        pygame.font.init()
    if _resolved["title"] is None:
        _resolved["title"] = _find_sysfont(_TITLE_CANDIDATES)
    if _resolved["body"] is None:
        _resolved["body"] = _find_sysfont(_BODY_CANDIDATES)
    if _resolved["file"] is None:
        _resolved["file"] = _find_font_file()


def get_font(size: int = 24, bold: bool = True, *, title: bool = False) -> pygame.font.Font:
    _resolve()
    family = _resolved["title"] if (title or size >= 36) else _resolved["body"]
    key = (family or _resolved["file"] or "default", size, bold)
    if key in _font_cache:
        return _font_cache[key]

    font: pygame.font.Font | None = None
    # Prefer TTF file for consistent cyber mono look
    if _resolved["file"]:
        try:
            font = pygame.font.Font(_resolved["file"], size)
        except Exception:
            font = None
    if font is None and family:
        try:
            font = pygame.font.SysFont(family, size, bold=bold)
        except Exception:
            font = None
    if font is None:
        font = pygame.font.Font(None, size)

    _font_cache[key] = font
    return font


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    size: int = 24,
    color: tuple[int, int, int] = WHITE_GLOW,
    center: bool = False,
    outline: bool = True,
    outline_color: tuple[int, int, int] = (0, 0, 0),
    outline_width: int | None = None,
    alpha: int = 255,
    *,
    title: bool = False,
) -> pygame.Rect:
    is_title = title or size >= 36
    font = get_font(size, bold=True, title=is_title)
    base = font.render(text, True, color)
    if alpha < 255:
        base = base.copy()
        base.set_alpha(alpha)

    if outline_width is None:
        ow = 3 if size >= 48 else 2 if size >= 26 else 1
    else:
        ow = outline_width

    if outline and ow > 0:
        w = base.get_width() + ow * 2
        h = base.get_height() + ow * 2
        canvas = pygame.Surface((w, h), pygame.SRCALPHA)
        outline_surf = font.render(text, True, outline_color)
        if alpha < 255:
            outline_surf = outline_surf.copy()
            outline_surf.set_alpha(min(255, alpha + 30))
        for dx, dy in (
            (-ow, 0),
            (ow, 0),
            (0, -ow),
            (0, ow),
            (-ow, -ow),
            (ow, -ow),
            (-ow, ow),
            (ow, ow),
        ):
            canvas.blit(outline_surf, (ow + dx, ow + dy))
        if ow >= 2:
            for dx, dy in ((-ow, 0), (ow, 0), (0, -ow), (0, ow)):
                canvas.blit(outline_surf, (ow + dx, ow + dy))
        canvas.blit(base, (ow, ow))
        final = canvas
        offset = ow
    else:
        final = base
        offset = 0

    rect = final.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = (pos[0] - offset, pos[1] - offset)
    surface.blit(final, rect)
    return rect


def measure(text: str, size: int = 24, *, title: bool = False) -> tuple[int, int]:
    font = get_font(size, bold=True, title=title or size >= 36)
    return font.size(text)


def clear_font_cache() -> None:
    _font_cache.clear()
    _resolved["title"] = None
    _resolved["body"] = None
    _resolved["file"] = None
