"""High scores table."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import CYAN, INTERNAL_H, INTERNAL_W, MAGENTA, WHITE_GLOW
from cipher.highscores import load_scores
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import draw_footer_hint, draw_header_bar, draw_panel
from cipher.scenes.base import Scene


class HighScoresScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.starfield = Starfield(4)
        self.t = 0.0
        self.scores = load_scores()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_ESCAPE,
            pygame.K_RETURN,
            pygame.K_SPACE,
            pygame.K_BACKSPACE,
        ):
            SFX.play("back")
            from cipher.scenes.main_menu import MainMenuScene

            self.app.replace_scene(MainMenuScene(self.app))

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "HIGH SCORES")
        panel = pygame.Rect(120, 130, INTERNAL_W - 240, 500)
        draw_panel(surface, panel)

        headers = f"{'#':<4}{'NAME':<6}{'PTS':>7}  {'MODE':<10}{'ARENA':<14}{'DIFF'}"
        draw_text(surface, headers, (panel.x + 28, panel.y + 28), 18, MAGENTA)

        if not self.scores:
            draw_text(
                surface,
                "NO SCORES YET — GO MAKE HISTORY",
                (INTERNAL_W // 2, INTERNAL_H // 2 + 20),
                24,
                WHITE_GLOW,
                center=True,
            )
        else:
            y = panel.y + 70
            for i, s in enumerate(self.scores):
                line = (
                    f"{i+1:<4}{s.name:<6}{s.points:>7}  {s.mode[:9]:<10}"
                    f"{s.arena[:13]:<14}{s.difficulty[:10]}"
                )
                col = CYAN if i == 0 else WHITE_GLOW
                draw_text(surface, line, (panel.x + 28, y), 18, col)
                y += 38

        draw_footer_hint(surface, "ESC / ENTER — BACK")
