"""Challenge mode intro / continue."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.sfx import SFX
from cipher.constants import (
    ARENA_NAMES,
    CHALLENGE_LADDER,
    CYAN,
    INTERNAL_H,
    INTERNAL_W,
    MAGENTA,
    WHITE_GLOW,
)
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import MenuList, draw_footer_hint, draw_header_bar, draw_panel
from cipher.scenes.base import Scene
from cipher.settings import load_progress, save_progress


class ChallengeIntroScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.starfield = Starfield(8)
        self.t = 0.0
        self.progress = load_progress()
        idx = min(self.progress.challenge_index, len(CHALLENGE_LADDER) - 1)
        self.menu = MenuList(
            ["CONTINUE LADDER", "RESTART LADDER", "BACK"],
            (INTERNAL_W // 2, INTERNAL_H // 2 + 80),
            width=380,
        )
        self.preview_index = idx

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
                SFX.play("back")
                from cipher.scenes.main_menu import MainMenuScene

                self.app.replace_scene(MainMenuScene(self.app))
        elif event.type == pygame.MOUSEMOTION:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu.set_hover(event.pos) is not None:
                self._act()

    def _act(self) -> None:
        choice = self.menu.current()
        if choice == "BACK":
            SFX.play("back")
            from cipher.scenes.main_menu import MainMenuScene

            self.app.replace_scene(MainMenuScene(self.app))
            return
        SFX.play("confirm")
        if choice == "RESTART LADDER":
            self.progress.challenge_index = 0
            save_progress(self.progress)
        idx = min(self.progress.challenge_index, len(CHALLENGE_LADDER) - 1)
        arena_id, diff = CHALLENGE_LADDER[idx]
        from cipher.scenes.match import MatchScene

        self.app.replace_scene(
            MatchScene(self.app),
            arena_id=arena_id,
            difficulty=diff,
            mode="challenge",
            challenge_index=idx,
        )

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        draw_header_bar(surface, "CHALLENGE MODE")
        panel = pygame.Rect(INTERNAL_W // 2 - 300, 140, 600, 200)
        draw_panel(surface, panel)
        idx = min(self.progress.challenge_index, len(CHALLENGE_LADDER) - 1)
        arena_id, diff = CHALLENGE_LADDER[idx]
        draw_text(surface, f"STAGE {idx + 1} / {len(CHALLENGE_LADDER)}", (INTERNAL_W // 2, 175), 22, MAGENTA, center=True)
        draw_text(
            surface,
            f"{ARENA_NAMES.get(arena_id, arena_id)} — {diff}",
            (INTERNAL_W // 2, 225),
            28,
            WHITE_GLOW,
            center=True,
        )
        draw_text(
            surface,
            f"BEST STREAK: {self.progress.best_streak}   UNLOCKED: {self.progress.unlocked_max + 1}",
            (INTERNAL_W // 2, 285),
            18,
            CYAN,
            center=True,
        )
        self.menu.draw(surface)
        draw_footer_hint(surface, "ENTER CONFIRM   ·   ESC BACK")
