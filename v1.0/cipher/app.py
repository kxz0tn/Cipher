"""Application shell: display scaling, scene stack, main loop."""
from __future__ import annotations

import atexit
from typing import Any

import pygame

from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.audio.shutdown import force_process_exit, shutdown_audio
from cipher.constants import (
    AUDIO_CHANNELS,
    BG_DEEP,
    FIXED_DT,
    INTERNAL_H,
    INTERNAL_W,
    SAMPLE_RATE,
    TARGET_FPS,
    WINDOW_TITLE,
)
from cipher.core.input import InputState
from cipher.core.timer import FixedTimer
from cipher.scenes.base import Scene
from cipher.scenes.title import TitleScene
from cipher.settings import Settings, load_settings, save_settings, user_data_dir


class App:
    def __init__(self) -> None:
        self.running = False
        self.settings: Settings = load_settings()
        if not (user_data_dir() / "settings.json").exists():
            self.settings.fullscreen = True
        self.input = InputState()
        self.timer = FixedTimer()
        self.scenes: list[Scene] = []
        self.virtual: pygame.Surface | None = None
        self.window: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.scale = 1
        self.offset = (0, 0)
        self.camera_offset = (0.0, 0.0)
        self._windowed_size = (INTERNAL_W, INTERNAL_H)
        self._exiting = False

    # ------------------------------------------------------------------ scene
    def push_scene(self, scene: Scene, **kwargs: Any) -> None:
        self.scenes.append(scene)
        scene.enter(**kwargs)

    def pop_scene(self) -> None:
        if not self.scenes:
            return
        top = self.scenes.pop()
        top.exit()

    def replace_scene(self, scene: Scene, **kwargs: Any) -> None:
        while self.scenes:
            self.pop_scene()
        self.push_scene(scene, **kwargs)

    def clear_scenes(self) -> None:
        while self.scenes:
            self.pop_scene()

    @property
    def scene(self) -> Scene | None:
        return self.scenes[-1] if self.scenes else None

    def quit(self) -> None:
        """Unified exit for Quit menu, window X, and Alt+F4."""
        if self._exiting:
            # Still force exit if a previous attempt stalled
            force_process_exit(0)
            return
        self._exiting = True
        self.running = False

        # Stop audio BEFORE anything else (even before save)
        try:
            MUSIC.hard_stop()
        except Exception:
            pass
        try:
            SFX.stop_all()
        except Exception:
            pass
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.stop()
                for i in range(32):
                    try:
                        pygame.mixer.Channel(i).set_volume(0)
                        pygame.mixer.Channel(i).stop()
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            save_settings(self.settings)
        except Exception:
            pass

        force_process_exit(0)

    # ---------------------------------------------------------------- display
    def set_fullscreen(self, enabled: bool) -> None:
        self.settings.fullscreen = enabled
        self._create_window()

    def toggle_fullscreen(self) -> None:
        self.set_fullscreen(not self.settings.fullscreen)
        save_settings(self.settings)

    def _create_window(self) -> None:
        flags = pygame.RESIZABLE
        if self.settings.fullscreen:
            info = pygame.display.Info()
            size = (info.current_w, info.current_h)
            self.window = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            size = self._windowed_size
            self.window = pygame.display.set_mode(size, flags)
        pygame.display.set_caption(WINDOW_TITLE)
        self._set_window_icon()
        self._recompute_scale()

    def _set_window_icon(self) -> None:
        """Window/taskbar icon from multi-size cipher.ico (user-replaced master)."""
        try:
            from pathlib import Path

            from cipher.render.assets import asset_path

            # Prefer packaged multi-size ico, then project root, then PNG masters
            candidates = [
                asset_path("cipher.ico"),
                Path(__file__).resolve().parent.parent / "cipher.ico",
                asset_path("logo_256.png"),
                asset_path("logo_48.png"),
            ]
            for path in candidates:
                if not path.is_file():
                    continue
                try:
                    icon = pygame.image.load(str(path)).convert_alpha()
                    w, h = icon.get_size()
                    if w != h:
                        side = max(w, h)
                        sq = pygame.Surface((side, side), pygame.SRCALPHA)
                        sq.blit(icon, ((side - w) // 2, (side - h) // 2))
                        icon = sq
                    if icon.get_width() > 256:
                        icon = pygame.transform.smoothscale(icon, (256, 256))
                    pygame.display.set_icon(icon)
                    return
                except pygame.error:
                    continue
        except Exception:
            pass

    def _recompute_scale(self) -> None:
        assert self.window is not None
        ww, wh = self.window.get_size()
        self.scale = max(1, min(ww // INTERNAL_W, wh // INTERNAL_H))
        self.offset = (
            (ww - INTERNAL_W * self.scale) // 2,
            (wh - INTERNAL_H * self.scale) // 2,
        )

    def window_to_virtual(self, pos: tuple[int, int]) -> tuple[int, int]:
        ox, oy = self.offset
        return (pos[0] - ox) // self.scale, (pos[1] - oy) // self.scale

    # ------------------------------------------------------------------- boot
    def run(self) -> int:
        atexit.register(lambda: shutdown_audio(force=True))

        pygame.mixer.pre_init(SAMPLE_RATE, size=-16, channels=2, buffer=512)
        pygame.init()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        except pygame.error:
            pass

        self.virtual = pygame.Surface((INTERNAL_W, INTERNAL_H))
        self.clock = pygame.time.Clock()
        self._create_window()

        SFX.bind_settings(self.settings)
        SFX.build()
        MUSIC.bind_settings(self.settings)

        self.running = True
        self.push_scene(TitleScene(self))

        try:
            while self.running:
                frame_ms = self.clock.tick(TARGET_FPS)
                frame_dt = frame_ms / 1000.0
                self._process_events()
                if not self.running or self._exiting:
                    break
                steps = self.timer.consume(frame_dt)
                scene = self.scene
                if scene:
                    for _ in range(steps):
                        scene.fixed_update(FIXED_DT)
                    scene.update(frame_dt)
                    self.virtual.fill(BG_DEEP)
                    scene.draw(self.virtual)
                self._present()
        finally:
            # Any exit that didn't already os._exit
            self.quit()
        return 0

    def _process_events(self) -> None:
        self.input.begin_frame()
        for event in pygame.event.get():
            # Window X and Alt+F4 both emit QUIT on Windows
            if event.type == pygame.QUIT:
                self.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            if event.type == pygame.VIDEORESIZE and not self.settings.fullscreen:
                self._windowed_size = (max(INTERNAL_W, event.w), max(INTERNAL_H, event.h))
                self._create_window()
                continue

            mapped = event
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                vx, vy = self.window_to_virtual(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    mapped = pygame.event.Event(
                        event.type,
                        {"pos": (vx, vy), "rel": event.rel, "buttons": event.buttons},
                    )
                else:
                    mapped = pygame.event.Event(
                        event.type,
                        {"pos": (vx, vy), "button": event.button},
                    )

            self.input.handle_event(mapped if mapped is not event else event)
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if self.scene:
                    self.scene.handle_event(event)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if self.scene:
                    self.scene.handle_event(mapped)
            else:
                if self.scene:
                    self.scene.handle_event(event)
        self.input.end_frame()

    def _present(self) -> None:
        assert self.window is not None and self.virtual is not None
        self.window.fill((0, 0, 0))
        scaled = pygame.transform.scale(
            self.virtual,
            (INTERNAL_W * self.scale, INTERNAL_H * self.scale),
        )
        ox, oy = self.offset
        cox = int(self.camera_offset[0] * self.scale)
        coy = int(self.camera_offset[1] * self.scale)
        self.window.blit(scaled, (ox + cox, oy + coy))
        pygame.display.flip()
