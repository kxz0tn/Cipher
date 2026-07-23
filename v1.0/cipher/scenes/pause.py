"""Pause overlay — premium sports chrome."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import CYAN, INTERNAL_H, INTERNAL_W, WHITE_GLOW
from cipher.render.font import draw_text
from cipher.render.palette import with_alpha
from cipher.render.ui import MenuList, draw_panel
from cipher.scenes.base import Scene


class PauseScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.match = kwargs.get("match")
        self.menu = MenuList(
            ["RESUME", "OPTIONS", "QUIT TO MENU"],
            (INTERNAL_W // 2, INTERNAL_H // 2 + 30),
            width=360,
            btn_h=50,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu.move(-1)
                SFX.play("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu.move(1)
                SFX.play("blip")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._act()
            elif event.key == pygame.K_ESCAPE:
                self._resume()
        elif event.type == pygame.MOUSEMOTION:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu.set_hover(event.pos) is not None:
                self._act()

    def _resume(self) -> None:
        SFX.play("back")
        if self.match is not None:
            self.match._paused = False
        self.app.pop_scene()

    def _act(self) -> None:
        choice = self.menu.current()
        if choice == "RESUME":
            self._resume()
        elif choice == "OPTIONS":
            SFX.play("confirm")
            from cipher.scenes.options import OptionsScene

            self.app.push_scene(OptionsScene(self.app))
        elif choice == "QUIT TO MENU":
            SFX.play("confirm")
            from cipher.scenes.main_menu import MainMenuScene

            self.app.clear_scenes()
            self.app.push_scene(MainMenuScene(self.app))

    def fixed_update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((INTERNAL_W, INTERNAL_H), pygame.SRCALPHA)
        overlay.fill(with_alpha((4, 1, 12), 175))
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(INTERNAL_W // 2 - 240, INTERNAL_H // 2 - 180, 480, 360)
        draw_panel(surface, panel)
        draw_text(surface, "PAUSED", (INTERNAL_W // 2, panel.y + 48), 42, CYAN, center=True)
        draw_text(
            surface,
            "MATCH SUSPENDED",
            (INTERNAL_W // 2, panel.y + 88),
            14,
            WHITE_GLOW,
            center=True,
            alpha=160,
        )
        self.menu.draw(surface)
