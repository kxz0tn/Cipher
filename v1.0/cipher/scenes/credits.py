"""Credits screen."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import CYAN, INTERNAL_H, INTERNAL_W, MAGENTA, PURPLE, VERSION, WHITE_GLOW
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import draw_footer_hint, draw_header_bar, draw_panel
from cipher.scenes.base import Scene


class CreditsScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.starfield = Starfield(5)
        self.t = 0.0
        self.lines = [
            ("CIPHER", CYAN, 36),
            (f"VERSION {VERSION}", WHITE_GLOW, 18),
            ("", WHITE_GLOW, 12),
            ("ORIGINAL CYBERPUNK ARENA SPORT", MAGENTA, 20),
            ("BUILT FOR THE CABINET SPIRIT", PURPLE, 18),
            ("", WHITE_GLOW, 12),
            ("ENGINE  ·  PYTHON + PYGAME-CE", WHITE_GLOW, 16),
            ("ART  ·  IMAGINE + PROCEDURAL SYSTEMS", WHITE_GLOW, 16),
            ("AUDIO  ·  PROCEDURAL CHIPTUNE SYNTH", WHITE_GLOW, 16),
            ("", WHITE_GLOW, 12),
            ("CHARACTERS · BALL · GOALS  —  ORIGINAL ASSETS", CYAN, 15),
            ("", WHITE_GLOW, 12),
            ("DASH  ·  CHARGE  ·  SCORE  ·  REPEAT", MAGENTA, 18),
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            SFX.play("back")
            from cipher.scenes.main_menu import MainMenuScene

            self.app.replace_scene(MainMenuScene(self.app))

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "CREDITS")
        panel = pygame.Rect(INTERNAL_W // 2 - 320, 140, 640, 460)
        draw_panel(surface, panel)
        y = panel.y + 40
        for text, col, size in self.lines:
            if text:
                draw_text(surface, text, (INTERNAL_W // 2, y), size, col, center=True)
            y += size + 12
        draw_footer_hint(surface, "PRESS ANY KEY — BACK")
