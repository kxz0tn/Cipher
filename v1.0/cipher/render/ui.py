"""Premium cyberpunk sports UI — panels, menus, scoreboard."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from cipher.constants import (
    CYAN,
    DARK_PANEL,
    MAGENTA,
    PANEL_BORDER,
    PURPLE,
    WHITE_GLOW,
    YELLOW,
)
from cipher.render.assets import load_image
from cipher.render.font import draw_text
from cipher.render.palette import darken, with_alpha


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    border_color: tuple[int, int, int] = PANEL_BORDER,
    fill: tuple[int, int, int] = DARK_PANEL,
    alpha: int = 220,
    sports: bool = True,
) -> None:
    """Draw a premium panel — uses baked chrome when available."""
    baked = load_image("menu_panel.png")
    if baked is not None and rect.w >= 200 and rect.h >= 120:
        scaled = pygame.transform.smoothscale(baked, rect.size)
        # darken interior slightly so text pops
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill(with_alpha((4, 2, 14), 90))
        surface.blit(scaled, rect.topleft)
        surface.blit(overlay, rect.topleft)
        # neon edge reinforce
        pygame.draw.rect(surface, with_alpha(border_color, 180), rect, 2, border_radius=8)
        return

    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, with_alpha(fill, alpha), panel.get_rect(), border_radius=8)
    if sports:
        pygame.draw.rect(panel, with_alpha(border_color, 255), panel.get_rect(), 3, border_radius=8)
        pygame.draw.rect(panel, with_alpha(CYAN, 100), panel.get_rect().inflate(-6, -6), 1, border_radius=5)
        for pt in ((8, 8), (rect.w - 9, 8), (8, rect.h - 9), (rect.w - 9, rect.h - 9)):
            pygame.draw.circle(panel, with_alpha(YELLOW, 230), pt, 3)
            pygame.draw.circle(panel, with_alpha(WHITE_GLOW, 255), pt, 1)
        # top accent bar
        pygame.draw.rect(panel, with_alpha(CYAN, 60), (10, 6, rect.w - 20, 3), border_radius=1)
        pygame.draw.rect(panel, with_alpha(MAGENTA, 50), (10, rect.h - 9, rect.w - 20, 3), border_radius=1)
    else:
        pygame.draw.rect(panel, with_alpha(border_color, 255), panel.get_rect(), 2, border_radius=8)
    surface.blit(panel, rect.topleft)


def draw_header_bar(surface: pygame.Surface, title: str, y: int = 0) -> None:
    """Top menu header strip."""
    header = load_image("menu_header.png")
    h = 100
    if header is not None:
        scaled = pygame.transform.smoothscale(header, (surface.get_width(), h))
        surface.blit(scaled, (0, y))
    else:
        bar = pygame.Surface((surface.get_width(), h), pygame.SRCALPHA)
        bar.fill(with_alpha((8, 4, 20), 210))
        surface.blit(bar, (0, y))
    # neon underline
    pygame.draw.line(
        surface,
        with_alpha(CYAN, 200),
        (40, y + h - 4),
        (surface.get_width() - 40, y + h - 4),
        2,
    )
    pygame.draw.line(
        surface,
        with_alpha(MAGENTA, 120),
        (80, y + h - 1),
        (surface.get_width() - 80, y + h - 1),
        1,
    )
    draw_text(surface, title, (surface.get_width() // 2, y + h // 2 + 4), 40, WHITE_GLOW, center=True)


@dataclass
class Button:
    label: str
    rect: pygame.Rect
    selected: bool = False
    hovered: bool = False

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface) -> None:
        active = self.selected or self.hovered
        normal = load_image("menu_button.png")
        hot = load_image("menu_button_hot.png")
        chrome = hot if active and hot is not None else normal
        if chrome is not None:
            scaled = pygame.transform.smoothscale(chrome, self.rect.size)
            surface.blit(scaled, self.rect.topleft)
            if active:
                # outer selection glow
                glow = pygame.Surface(self.rect.inflate(10, 10).size, pygame.SRCALPHA)
                pygame.draw.rect(
                    glow,
                    with_alpha(CYAN, 50),
                    glow.get_rect(),
                    border_radius=8,
                )
                surface.blit(glow, self.rect.move(-5, -5).topleft)
        else:
            border = CYAN if active else PANEL_BORDER
            fill = darken(PURPLE, 0.28) if active else DARK_PANEL
            draw_panel(surface, self.rect, border_color=border, fill=fill, alpha=240 if active else 210)

        if active:
            draw_text(surface, "▶", (self.rect.left + 22, self.rect.centery), 18, YELLOW, center=True)
            draw_text(surface, "◀", (self.rect.right - 22, self.rect.centery), 18, YELLOW, center=True)
        color = WHITE_GLOW if active else (175, 185, 205)
        draw_text(surface, self.label, self.rect.center, 24, color, center=True)


class MenuList:
    def __init__(
        self,
        labels: list[str],
        center: tuple[int, int],
        width: int = 400,
        btn_h: int = 52,
        gap: int = 14,
    ) -> None:
        self.labels = labels
        self.index = 0
        self.buttons: list[Button] = []
        total_h = len(labels) * btn_h + max(0, len(labels) - 1) * gap
        start_y = center[1] - total_h // 2
        for i, label in enumerate(labels):
            r = pygame.Rect(0, 0, width, btn_h)
            r.centerx = center[0]
            r.y = start_y + i * (btn_h + gap)
            self.buttons.append(Button(label, r, selected=(i == 0)))

    def move(self, delta: int) -> None:
        if not self.buttons:
            return
        self.index = (self.index + delta) % len(self.buttons)
        for i, b in enumerate(self.buttons):
            b.selected = i == self.index

    def set_hover(self, pos: tuple[int, int]) -> int | None:
        hit = None
        for i, b in enumerate(self.buttons):
            b.hovered = b.contains(pos)
            if b.hovered:
                hit = i
                self.index = i
                for j, bb in enumerate(self.buttons):
                    bb.selected = j == i
        return hit

    def current(self) -> str:
        return self.labels[self.index]

    def draw(self, surface: pygame.Surface) -> None:
        for b in self.buttons:
            b.draw(surface)


@dataclass
class Slider:
    label: str
    rect: pygame.Rect
    value: float
    selected: bool = False

    def handle_click(self, pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            rel = (pos[0] - self.rect.x) / max(self.rect.w, 1)
            self.value = max(0.0, min(1.0, rel))
            return True
        return False

    def adjust(self, delta: float) -> None:
        self.value = max(0.0, min(1.0, self.value + delta))

    def draw(self, surface: pygame.Surface) -> None:
        draw_text(
            surface,
            self.label,
            (self.rect.x, self.rect.y - 26),
            20,
            CYAN if self.selected else WHITE_GLOW,
        )
        track = self.rect
        pygame.draw.rect(surface, with_alpha(DARK_PANEL, 240), track, border_radius=5)
        pygame.draw.rect(surface, with_alpha(CYAN if self.selected else PANEL_BORDER, 255), track, 2, border_radius=5)
        fill_w = int(track.w * self.value)
        if fill_w > 0:
            fill = pygame.Rect(track.x, track.y, fill_w, track.h)
            col = CYAN if self.selected else MAGENTA
            pygame.draw.rect(surface, with_alpha(col, 220), fill, border_radius=5)
            pygame.draw.line(
                surface,
                with_alpha(WHITE_GLOW, 120),
                (fill.left + 3, fill.top + 3),
                (fill.right - 3, fill.top + 3),
                1,
            )
        kx = track.x + fill_w
        pygame.draw.circle(surface, WHITE_GLOW, (kx, track.centery), 9)
        pygame.draw.circle(surface, YELLOW, (kx, track.centery), 4)
        draw_text(surface, f"{int(self.value * 100)}%", (track.right + 14, track.y), 18, WHITE_GLOW)


def draw_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    value: float,
    color: tuple[int, int, int],
    back: tuple[int, int, int] = DARK_PANEL,
) -> None:
    value = max(0.0, min(1.0, value))
    pygame.draw.rect(surface, with_alpha(back, 220), rect, border_radius=4)
    if value > 0:
        fr = pygame.Rect(rect.x, rect.y, max(2, int(rect.w * value)), rect.h)
        pygame.draw.rect(surface, with_alpha(color, 240), fr, border_radius=4)
        if fr.w > 6:
            pygame.draw.line(
                surface,
                with_alpha(WHITE_GLOW, 110),
                (fr.left + 2, fr.top + 2),
                (fr.right - 2, fr.top + 2),
                1,
            )
    pygame.draw.rect(surface, with_alpha(WHITE_GLOW, 140), rect, 1, border_radius=4)


def draw_logo(surface: pygame.Surface, center: tuple[int, int], t: float, scale: float = 1.0) -> None:
    """Menu header mark — clean logo.png only (no glow, bob, or effects)."""
    import math

    logo = load_image("logo.png")
    if logo is not None:
        max_w = int(220 * scale)
        max_h = int(120 * scale)
        lw, lh = logo.get_size()
        sc = min(max_w / max(lw, 1), max_h / max(lh, 1))
        nw, nh = max(1, int(lw * sc)), max(1, int(lh * sc))
        if (nw, nh) != (lw, lh):
            logo = pygame.transform.smoothscale(logo, (nw, nh))
        # Plain centered blit — no bob / glow / filters
        surface.blit(logo, logo.get_rect(center=center))
        return

    title = "CIPHER"
    size = int(48 * scale)
    pulse = 0.5 + 0.5 * abs(math.sin(t * 2.0))
    for i, col in enumerate((PURPLE, MAGENTA, CYAN)):
        ox = int(math.sin(t * 1.3 + i) * 2)
        draw_text(
            surface,
            title,
            (center[0] + ox, center[1]),
            size,
            col,
            center=True,
            outline=False,
            alpha=int(35 + pulse * 40),
        )
    draw_text(surface, title, center, size, WHITE_GLOW, center=True)
    draw_text(
        surface,
        "NEON ARENA SPORTS",
        (center[0], center[1] + int(28 * scale)),
        int(13 * scale),
        CYAN,
        center=True,
        alpha=200,
    )


def format_match_clock(seconds: float) -> str:
    """Format remaining seconds as MM:SS (ceil so last second shows until true zero)."""
    import math

    if seconds <= 0:
        total = 0
    else:
        total = max(0, int(math.ceil(seconds - 1e-9)))
    m, s = divmod(total, 60)
    return f"{m:02d}:{s:02d}"


def draw_match_hud_header(
    surface: pygame.Surface,
    home_score: int,
    away_score: int,
    home_name: str,
    away_name: str,
    time_remaining: float,
    arena_label: str,
    difficulty_label: str,
) -> None:
    """Clean non-overlapping scoreboard + countdown timer + info strip."""
    from cipher.constants import DANGER, INTERNAL_W

    # Main board
    board = pygame.Rect(INTERNAL_W // 2 - 210, 8, 420, 52)
    draw_panel(surface, board, border_color=PURPLE, fill=DARK_PANEL, alpha=235)
    pygame.draw.rect(surface, with_alpha(CYAN, 220), (board.left + 8, board.top + 10, 4, board.h - 20))
    pygame.draw.rect(surface, with_alpha(MAGENTA, 220), (board.right - 12, board.top + 10, 4, board.h - 20))

    draw_text(surface, home_name[:6], (board.left + 48, board.centery), 15, CYAN, center=True)
    draw_text(surface, str(home_score), (board.centerx - 78, board.centery), 34, CYAN, center=True)
    draw_text(surface, "–", (board.centerx, board.centery), 28, WHITE_GLOW, center=True)
    draw_text(surface, str(away_score), (board.centerx + 78, board.centery), 34, MAGENTA, center=True)
    draw_text(surface, away_name[:6], (board.right - 48, board.centery), 15, MAGENTA, center=True)

    # Timer band — fully below scoreboard
    clock = format_match_clock(time_remaining)
    urgent = time_remaining <= 30.0
    timer = pygame.Rect(0, 0, 132, 30)
    timer.midtop = (INTERNAL_W // 2, board.bottom + 8)
    pygame.draw.rect(surface, with_alpha(DARK_PANEL, 245), timer, border_radius=4)
    border_col = DANGER if urgent else YELLOW
    pygame.draw.rect(surface, with_alpha(border_col, 230), timer, 2, border_radius=4)
    draw_text(surface, clock, timer.center, 20, border_col, center=True)

    # Info — below timer with clear gap
    draw_text(
        surface,
        f"{arena_label}  ·  {difficulty_label}",
        (INTERNAL_W // 2, timer.bottom + 16),
        13,
        WHITE_GLOW,
        center=True,
        alpha=170,
    )


def draw_sports_scoreboard(
    surface: pygame.Surface,
    rect: pygame.Rect,
    home_score: int,
    away_score: int,
    home_name: str = "VEX",
    away_name: str = "FOE",
    match_time: float | None = None,
) -> None:
    """Legacy scoreboard helper (kept for compatibility). Prefer draw_match_hud_header."""
    draw_panel(surface, rect, border_color=PURPLE, fill=DARK_PANEL, alpha=235)
    pygame.draw.rect(surface, with_alpha(CYAN, 200), (rect.left + 6, rect.top + 8, 5, rect.h - 16))
    pygame.draw.rect(surface, with_alpha(MAGENTA, 200), (rect.right - 11, rect.top + 8, 5, rect.h - 16))
    draw_text(surface, home_name, (rect.left + 52, rect.centery), 16, CYAN, center=True)
    draw_text(surface, str(home_score), (rect.centerx - 70, rect.centery), 36, CYAN, center=True)
    draw_text(surface, "–", (rect.centerx, rect.centery), 26, WHITE_GLOW, center=True)
    draw_text(surface, str(away_score), (rect.centerx + 70, rect.centery), 36, MAGENTA, center=True)
    draw_text(surface, away_name, (rect.right - 55, rect.centery), 16, MAGENTA, center=True)
    if match_time is not None:
        clock = format_match_clock(match_time)
        tr = pygame.Rect(0, 0, 120, 28)
        tr.midtop = (rect.centerx, rect.bottom + 6)
        pygame.draw.rect(surface, with_alpha(DARK_PANEL, 230), tr, border_radius=4)
        pygame.draw.rect(surface, with_alpha(CYAN, 200), tr, 1, border_radius=4)
        draw_text(surface, clock, tr.center, 20, YELLOW, center=True)


def draw_footer_hint(surface: pygame.Surface, text: str) -> None:
    draw_text(
        surface,
        text,
        (surface.get_width() // 2, surface.get_height() - 32),
        15,
        WHITE_GLOW,
        center=True,
        alpha=160,
    )
