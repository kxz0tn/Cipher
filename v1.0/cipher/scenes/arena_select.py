"""Arena and difficulty selection for Quick Match."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import (
    ARENA_IDS,
    ARENA_NAMES,
    CYAN,
    DIFFICULTIES,
    INTERNAL_H,
    INTERNAL_W,
    MAGENTA,
    WHITE_GLOW,
)
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import MenuList, draw_footer_hint, draw_header_bar
from cipher.scenes.base import Scene
from cipher.settings import save_settings


class ArenaSelectScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.mode = kwargs.get("mode", "quick")
        self.starfield = Starfield(6)
        self.t = 0.0
        labels = [ARENA_NAMES[a].upper() for a in ARENA_IDS]
        self.menu = MenuList(labels, (INTERNAL_W // 2, INTERNAL_H // 2 + 20), width=420, btn_h=52)
        # restore last
        last = self.app.settings.last_arena
        if last in ARENA_IDS:
            self.menu.index = ARENA_IDS.index(last)
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
                SFX.play("confirm")
                arena_id = ARENA_IDS[self.menu.index]
                self.app.settings.last_arena = arena_id
                save_settings(self.app.settings)
                from cipher.scenes.difficulty_select import DifficultySelectScene

                self.app.replace_scene(
                    DifficultySelectScene(self.app),
                    mode=self.mode,
                    arena_id=arena_id,
                )
            elif event.key == pygame.K_ESCAPE:
                SFX.play("back")
                from cipher.scenes.main_menu import MainMenuScene

                self.app.replace_scene(MainMenuScene(self.app))
        elif event.type == pygame.MOUSEMOTION:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu.set_hover(event.pos) is not None:
                SFX.play("confirm")
                arena_id = ARENA_IDS[self.menu.index]
                from cipher.scenes.difficulty_select import DifficultySelectScene

                self.app.replace_scene(
                    DifficultySelectScene(self.app),
                    mode=self.mode,
                    arena_id=arena_id,
                )

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "SELECT ARENA")
        self.menu.draw(surface)
        aid = ARENA_IDS[self.menu.index]
        blurbs = {
            "neon_sphere": "Clean neon pitch. Pure skill. No excuses.",
            "debris_field": "Asteroids and energy barriers. Time the chaos.",
            "gravity_well": "Central pull and lethal rings. Bank your shots.",
        }
        draw_text(
            surface,
            blurbs.get(aid, ""),
            (INTERNAL_W // 2, INTERNAL_H - 90),
            18,
            MAGENTA,
            center=True,
        )
        draw_footer_hint(surface, "ENTER CONFIRM   ·   ESC BACK")
