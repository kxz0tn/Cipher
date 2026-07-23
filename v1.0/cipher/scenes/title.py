"""Title screen — exact logo.png centered, no effects on the logo."""
from __future__ import annotations

import random
from typing import Any

import pygame

from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.constants import CYAN, INTERNAL_H, INTERNAL_W, MAGENTA, VERSION, WHITE_GLOW
from cipher.render.assets import clear_asset_cache, load_image
from cipher.render.backgrounds import draw_title_background
from cipher.render.font import draw_text
from cipher.render.fx import ParticleSystem
from cipher.render.palette import with_alpha
from cipher.scenes.base import Scene


class TitleScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        clear_asset_cache()  # pick up exact logo.png
        self.particles = ParticleSystem()
        self.t = 0.0
        self.blink = 0.0
        MUSIC.play("title")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                SFX.play("confirm")
                from cipher.scenes.main_menu import MainMenuScene

                self.app.replace_scene(MainMenuScene(self.app))
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()

    def fixed_update(self, dt: float) -> None:
        self.t += dt
        self.blink += dt
        self.particles.update(dt)
        if int(self.t * 8) % 15 == 0:
            self.particles.emit(
                random.randint(80, INTERNAL_W - 80),
                random.randint(50, INTERNAL_H // 2 + 40),
                2,
                CYAN if random.random() < 0.5 else MAGENTA,
                speed=22,
                life=1.2,
                size=1.8,
            )

    def draw(self, surface: pygame.Surface) -> None:
        draw_title_background(surface, self.t)
        self.particles.draw(surface)

        # Exact logo.png — plain centered blit only (no glow / filters / frames)
        logo = load_image("logo.png")
        logo_center = (INTERNAL_W // 2, INTERNAL_H // 2 - 90)
        if logo is not None:
            # Fit to screen only so the full logo is visible; no other processing
            max_w, max_h = 620, 360
            lw, lh = logo.get_size()
            if lw > max_w or lh > max_h:
                sc = min(max_w / max(lw, 1), max_h / max(lh, 1))
                nw, nh = max(1, int(lw * sc)), max(1, int(lh * sc))
                logo = pygame.transform.smoothscale(logo, (nw, nh))
            surface.blit(logo, logo.get_rect(center=logo_center))

        # Neon CIPHER title (not white, not glitch)
        neon = (0, 245, 255)  # electric cyan
        draw_text(
            surface,
            "CIPHER",
            (INTERNAL_W // 2 + 2, INTERNAL_H // 2 + 110),
            48,
            MAGENTA,
            center=True,
            outline=False,
            alpha=140,
            title=True,
        )
        draw_text(
            surface,
            "CIPHER",
            (INTERNAL_W // 2, INTERNAL_H // 2 + 108),
            48,
            neon,
            center=True,
            outline=True,
            outline_color=(0, 20, 40),
            outline_width=3,
            title=True,
        )

        draw_text(
            surface,
            "NEON ARENA SPORT",
            (INTERNAL_W // 2, INTERNAL_H // 2 + 150),
            16,
            MAGENTA,
            center=True,
        )
        draw_text(
            surface,
            "SCORE   ·   DEFEND   ·   DOMINATE",
            (INTERNAL_W // 2, INTERNAL_H // 2 + 174),
            13,
            (160, 150, 190),
            center=True,
            alpha=210,
        )

        if int(self.blink * 1.8) % 2 == 0:
            plate = pygame.Rect(0, 0, 240, 38)
            plate.center = (INTERNAL_W // 2, INTERNAL_H // 2 + 220)
            pygame.draw.rect(surface, with_alpha((4, 2, 12), 220), plate, border_radius=3)
            pygame.draw.rect(surface, with_alpha(CYAN, 180), plate, 1, border_radius=3)
            draw_text(surface, "PRESS ENTER", plate.center, 20, WHITE_GLOW, center=True)

        draw_text(
            surface,
            f"v{VERSION}",
            (INTERNAL_W // 2, INTERNAL_H - 32),
            13,
            (120, 120, 140),
            center=True,
            alpha=160,
            outline=False,
        )
