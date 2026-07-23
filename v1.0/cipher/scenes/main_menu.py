"""Premium main menu."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.constants import INTERNAL_H, INTERNAL_W
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.ui import MenuList, draw_footer_hint, draw_logo
from cipher.scenes.base import Scene


class MainMenuScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.starfield = Starfield(2)
        self.t = 0.0
        self.menu = MenuList(
            ["QUICK MATCH", "CHALLENGE MODE", "OPTIONS", "HIGH SCORES", "CREDITS", "QUIT"],
            (INTERNAL_W // 2, INTERNAL_H // 2 + 55),
            width=420,
            btn_h=52,
            gap=12,
        )
        MUSIC.play("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu.move(-1)
                SFX.play("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu.move(1)
                SFX.play("blip")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self._activate()
            elif event.key == pygame.K_ESCAPE:
                from cipher.scenes.title import TitleScene

                SFX.play("back")
                self.app.replace_scene(TitleScene(self.app))
        elif event.type == pygame.MOUSEMOTION:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu.set_hover(event.pos) is not None:
                self._activate()

    def _activate(self) -> None:
        choice = self.menu.current()
        # Quit must not play SFX first — go straight to hard audio kill
        if choice == "QUIT":
            self.app.quit()
            return
        SFX.play("confirm")
        if choice == "QUICK MATCH":
            from cipher.scenes.arena_select import ArenaSelectScene

            self.app.replace_scene(ArenaSelectScene(self.app), mode="quick")
        elif choice == "CHALLENGE MODE":
            from cipher.scenes.mode_select import ChallengeIntroScene

            self.app.replace_scene(ChallengeIntroScene(self.app))
        elif choice == "OPTIONS":
            from cipher.scenes.options import OptionsScene

            self.app.push_scene(OptionsScene(self.app))
        elif choice == "HIGH SCORES":
            from cipher.scenes.highscores_scene import HighScoresScene

            self.app.replace_scene(HighScoresScene(self.app))
        elif choice == "CREDITS":
            from cipher.scenes.credits import CreditsScene

            self.app.replace_scene(CreditsScene(self.app))

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_logo(surface, (INTERNAL_W // 2, 95), self.t, scale=0.62)
        self.menu.draw(surface)
        draw_footer_hint(surface, "ARROWS / WASD   ·   ENTER   ·   ESC")
