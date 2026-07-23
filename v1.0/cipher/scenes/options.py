"""Options menu: volume, fullscreen, controls."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.constants import CYAN, INTERNAL_H, INTERNAL_W, WHITE_GLOW, YELLOW
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import Slider, draw_footer_hint, draw_header_bar, draw_panel
from cipher.scenes.base import Scene
from cipher.settings import save_settings


class OptionsScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.starfield = Starfield(3)
        self.t = 0.0
        s = self.app.settings
        cx = INTERNAL_W // 2
        self.sliders = [
            Slider("MASTER VOLUME", pygame.Rect(cx - 180, 210, 360, 18), s.master_volume, True),
            Slider("MUSIC VOLUME", pygame.Rect(cx - 180, 285, 360, 18), s.music_volume),
            Slider("SFX VOLUME", pygame.Rect(cx - 180, 360, 360, 18), s.sfx_volume),
        ]
        self.index = 0
        self.fullscreen = s.fullscreen
        self.items = ["master", "music", "sfx", "fullscreen", "back"]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.items)
                SFX.play("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.items)
                SFX.play("blip")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-0.05)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(0.05)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.items[self.index] == "fullscreen":
                    self.fullscreen = not self.fullscreen
                    self.app.set_fullscreen(self.fullscreen)
                    SFX.play("confirm")
                elif self.items[self.index] == "back":
                    self._save_and_back()
            elif event.key == pygame.K_ESCAPE:
                self._save_and_back()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, sl in enumerate(self.sliders):
                if sl.handle_click(event.pos):
                    self.index = i
                    self._apply_volumes()
                    SFX.play("blip")

    def _adjust(self, delta: float) -> None:
        item = self.items[self.index]
        if item == "master":
            self.sliders[0].adjust(delta)
            self._apply_volumes()
            SFX.play("blip")
        elif item == "music":
            self.sliders[1].adjust(delta)
            self._apply_volumes()
        elif item == "sfx":
            self.sliders[2].adjust(delta)
            self._apply_volumes()
            SFX.play("blip")
        elif item == "fullscreen":
            self.fullscreen = not self.fullscreen
            self.app.set_fullscreen(self.fullscreen)
            SFX.play("confirm")

    def _apply_volumes(self) -> None:
        s = self.app.settings
        s.master_volume = self.sliders[0].value
        s.music_volume = self.sliders[1].value
        s.sfx_volume = self.sliders[2].value
        s.clamp()
        MUSIC.update_volume()
        SFX.bind_settings(s)

    def _save_and_back(self) -> None:
        self._apply_volumes()
        self.app.settings.fullscreen = self.fullscreen
        save_settings(self.app.settings)
        SFX.play("back")
        self.app.pop_scene()

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)
        for i, sl in enumerate(self.sliders):
            sl.selected = self.index == i

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "OPTIONS")
        panel = pygame.Rect(INTERNAL_W // 2 - 300, 130, 600, 480)
        draw_panel(surface, panel)

        for sl in self.sliders:
            sl.draw(surface)

        fs_label = f"FULLSCREEN: {'ON' if self.fullscreen else 'OFF'}   (ENTER)"
        col = CYAN if self.index == 3 else WHITE_GLOW
        draw_text(surface, fs_label, (INTERNAL_W // 2, 430), 22, col, center=True)

        back_col = YELLOW if self.index == 4 else WHITE_GLOW
        draw_text(surface, "◀  BACK", (INTERNAL_W // 2, 475), 24, back_col, center=True)

        draw_text(surface, "CONTROLS", (INTERNAL_W // 2, 520), 16, CYAN, center=True)
        draw_text(
            surface,
            "MOVE WASD/ARROWS  ·  DASH SHIFT  ·  CHARGE SPACE  ·  PAUSE ESC  ·  F11 FULLSCREEN",
            (INTERNAL_W // 2, 550),
            13,
            WHITE_GLOW,
            center=True,
            alpha=180,
        )
        draw_footer_hint(surface, "ARROWS ADJUST   ·   ESC SAVE & BACK")
