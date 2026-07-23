"""Post-match results and high score entry."""
from __future__ import annotations

from typing import Any

import pygame

from cipher.audio.music import MUSIC
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
from cipher.highscores import insert_score, make_entry, name_exists, qualifies
from cipher.render.backgrounds import Starfield, draw_menu_background
from cipher.render.font import draw_text
from cipher.render.ui import MenuList, draw_footer_hint, draw_header_bar, draw_panel
from cipher.scenes.base import Scene
from cipher.settings import load_progress, save_progress


class ResultsScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.won = bool(kwargs.get("won", False))
        self.player_score = int(kwargs.get("player_score", 0))
        self.enemy_score = int(kwargs.get("enemy_score", 0))
        self.points = int(kwargs.get("points", 0))
        self.mode = kwargs.get("mode", "quick")
        self.arena_id = kwargs.get("arena_id", "neon_sphere")
        self.difficulty = kwargs.get("difficulty", "Operative")
        self.challenge_index = int(kwargs.get("challenge_index", 0))
        self.match_time = float(kwargs.get("match_time", 0))

        self.starfield = Starfield(9)
        self.t = 0.0

        # High scores only when the player wins (never loss / draw)
        self.entering_name = self.won and qualifies(self.points, won=True)
        self.name_chars = ["A", "A", "A"]
        self.name_index = 0
        self.saved = False
        self.name_taken_msg = 0.0  # seconds remaining for "name taken" feedback

        labels = []
        if self.mode == "challenge" and self.won:
            if self.challenge_index + 1 < len(CHALLENGE_LADDER):
                labels.append("NEXT STAGE")
            else:
                labels.append("LADDER COMPLETE")
        if self.mode == "quick":
            labels.append("REMATCH")
        labels.extend(["MAIN MENU", "HIGH SCORES"])
        self.menu = MenuList(labels, (INTERNAL_W // 2, INTERNAL_H // 2 + 140), width=340)

        if self.mode == "challenge":
            progress = load_progress()
            if self.won:
                nxt = self.challenge_index + 1
                progress.challenge_index = min(nxt, len(CHALLENGE_LADDER) - 1)
                progress.unlocked_max = max(progress.unlocked_max, self.challenge_index)
                progress.best_streak = max(progress.best_streak, nxt)
                if nxt >= len(CHALLENGE_LADDER):
                    progress.challenge_index = 0  # completed — allow restart from menu
            else:
                # stay on same stage
                pass
            save_progress(progress)

        MUSIC.play("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.entering_name and not self.saved:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.name_index = (self.name_index - 1) % 3
                    self.name_taken_msg = 0.0
                    SFX.play("blip")
                elif event.key == pygame.K_RIGHT:
                    self.name_index = (self.name_index + 1) % 3
                    self.name_taken_msg = 0.0
                    SFX.play("blip")
                elif event.key == pygame.K_UP:
                    c = self.name_chars[self.name_index]
                    self.name_chars[self.name_index] = chr((ord(c) - 65 + 1) % 26 + 65)
                    self.name_taken_msg = 0.0
                    SFX.play("blip")
                elif event.key == pygame.K_DOWN:
                    c = self.name_chars[self.name_index]
                    self.name_chars[self.name_index] = chr((ord(c) - 65 - 1) % 26 + 65)
                    self.name_taken_msg = 0.0
                    SFX.play("blip")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._save_score()
                return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu.move(-1)
                SFX.play("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu.move(1)
                SFX.play("blip")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._menu_act()
            elif event.key == pygame.K_ESCAPE:
                self._to_menu()
        elif event.type == pygame.MOUSEMOTION and not self.entering_name:
            self.menu.set_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.entering_name:
            if self.menu.set_hover(event.pos) is not None:
                self._menu_act()

    def _save_score(self) -> None:
        # Never persist high scores unless this was a win
        if not self.won:
            self.entering_name = False
            return
        name = "".join(self.name_chars)
        if name_exists(name):
            # Do not save — name already on the board
            self.name_taken_msg = 3.0
            SFX.play("blip", 0.7)
            return
        entry = make_entry(
            name,
            self.points,
            "Challenge" if self.mode == "challenge" else "Quick",
            ARENA_NAMES.get(self.arena_id, self.arena_id),
            self.difficulty,
            self.player_score,
            self.enemy_score,
        )
        result = insert_score(entry, won=True)
        if result is None:
            self.name_taken_msg = 3.0
            SFX.play("blip", 0.7)
            return
        self.saved = True
        self.entering_name = False
        self.name_taken_msg = 0.0
        SFX.play("confirm")

    def _menu_act(self) -> None:
        if self.entering_name and not self.saved:
            self._save_score()
            return
        SFX.play("confirm")
        choice = self.menu.current()
        if choice == "REMATCH":
            from cipher.scenes.match import MatchScene

            self.app.replace_scene(
                MatchScene(self.app),
                arena_id=self.arena_id,
                difficulty=self.difficulty,
                mode="quick",
            )
        elif choice == "NEXT STAGE":
            nxt = self.challenge_index + 1
            if nxt < len(CHALLENGE_LADDER):
                arena_id, diff = CHALLENGE_LADDER[nxt]
                from cipher.scenes.match import MatchScene

                self.app.replace_scene(
                    MatchScene(self.app),
                    arena_id=arena_id,
                    difficulty=diff,
                    mode="challenge",
                    challenge_index=nxt,
                )
            else:
                self._to_menu()
        elif choice == "LADDER COMPLETE":
            self._to_menu()
        elif choice == "HIGH SCORES":
            from cipher.scenes.highscores_scene import HighScoresScene

            self.app.replace_scene(HighScoresScene(self.app))
        else:
            self._to_menu()

    def _to_menu(self) -> None:
        from cipher.scenes.main_menu import MainMenuScene

        self.app.replace_scene(MainMenuScene(self.app))

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.starfield.update(dt)
        if self.name_taken_msg > 0:
            self.name_taken_msg = max(0.0, self.name_taken_msg - dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.starfield, self.t)
        if self.won:
            title = "VICTORY"
        elif self.player_score == self.enemy_score:
            title = "DRAW"
        else:
            title = "DEFEAT"
        draw_header_bar(surface, title)

        panel = pygame.Rect(INTERNAL_W // 2 - 280, 140, 560, 240)
        draw_panel(surface, panel)
        draw_text(
            surface,
            f"{self.player_score}  -  {self.enemy_score}",
            (INTERNAL_W // 2, 200),
            52,
            WHITE_GLOW,
            center=True,
        )
        draw_text(
            surface,
            f"{ARENA_NAMES.get(self.arena_id, '')}  ·  {self.difficulty}",
            (INTERNAL_W // 2, 260),
            20,
            MAGENTA,
            center=True,
        )
        draw_text(surface, f"SCORE  {self.points}", (INTERNAL_W // 2, 310), 30, CYAN, center=True)

        if self.entering_name and not self.saved:
            draw_text(surface, "NEW HIGH SCORE — ENTER NAME", (INTERNAL_W // 2, 400), 20, CYAN, center=True)
            for i, ch in enumerate(self.name_chars):
                x = INTERNAL_W // 2 - 40 + i * 40
                c = CYAN if i == self.name_index else WHITE_GLOW
                draw_text(surface, ch, (x, 445), 40, c, center=True)
                if i == self.name_index:
                    draw_text(surface, "^", (x, 485), 20, CYAN, center=True)
            if self.name_taken_msg > 0:
                draw_text(
                    surface,
                    "NAME ALREADY TAKEN",
                    (INTERNAL_W // 2, 520),
                    22,
                    MAGENTA,
                    center=True,
                )
                draw_text(
                    surface,
                    "ENTER A DIFFERENT NAME",
                    (INTERNAL_W // 2, 548),
                    16,
                    WHITE_GLOW,
                    center=True,
                )
                draw_footer_hint(surface, "ARROWS CHANGE   ·   ENTER TO RETRY")
            else:
                draw_footer_hint(surface, "ARROWS CHANGE   ·   ENTER CONFIRM")
        else:
            self.menu.draw(surface)
            draw_footer_hint(surface, "ENTER SELECT")
