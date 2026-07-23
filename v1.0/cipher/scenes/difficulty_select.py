"""Difficulty selection."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import CYAN, DIFFICULTIES, INTERNAL_H, INTERNAL_W, MAGENTA, WHITE_GLOW
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import MenuList, draw_footer_hint, draw_header_bar
from cipher.scenes.base import Scene
from cipher.settings import save_settings


class DifficultySelectScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.mode = kwargs.get("mode", "quick")
        self.arena_id = kwargs.get("arena_id", "neon_sphere")
        self.starfield = Starfield(7)
        self.t = 0.0
        self.menu = MenuList(
            [d.upper() for d in DIFFICULTIES],
            (INTERNAL_W // 2, INTERNAL_H // 2 + 20),
            width=400,
            btn_h=52,
        )
        last = self.app.settings.last_difficulty
        if last in DIFFICULTIES:
            self.menu.index = DIFFICULTIES.index(last)
            self.menu.move(0)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu.move(-1)
                SFX.play("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu.move(1)
                SFX.play("blip")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start()
            elif event.key == pygame.K_ESCAPE:
                SFX.play("back")
                from cipher.scenes.arena_select import ArenaSelectScene

                self.app.replace_scene(ArenaSelectScene(self.app), mode=self.mode)
        elif event.type == pygame.MOUSEMOTION:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu.set_hover(event.pos) is not None:
                self._start()

    def _start(self) -> None:
        SFX.play("confirm")
        diff = DIFFICULTIES[self.menu.index]
        self.app.settings.last_difficulty = diff
        save_settings(self.app.settings)
        from cipher.scenes.match import MatchScene

        self.app.replace_scene(
            MatchScene(self.app),
            arena_id=self.arena_id,
            difficulty=diff,
            mode=self.mode,
        )

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "SELECT DIFFICULTY")
        self.menu.draw(surface)
        blurbs = {
            "Initiate": "Learn the arena. Forgive the chaos.",
            "Operative": "Standard threat profile. Fair fight.",
            "Phantom": "Fast AI. Tight windows. Bring skill.",
            "Nightmare": "No mercy. Predictive intercepts.",
        }
        d = DIFFICULTIES[self.menu.index]
        draw_text(surface, blurbs[d], (INTERNAL_W // 2, INTERNAL_H - 90), 18, MAGENTA, center=True)
        draw_footer_hint(surface, "ENTER START   ·   ESC BACK")
