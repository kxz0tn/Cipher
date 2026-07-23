"""Keyboard input mapping with edge detection."""
from __future__ import annotations

import pygame

from cipher.core.math_util import normalize


class InputState:
    def __init__(self) -> None:
        self.move_x = 0.0
        self.move_y = 0.0
        self.dash_pressed = False
        self.hit_held = False
        self.hit_pressed = False
        self.hit_released = False
        self.pause_pressed = False
        self.confirm_pressed = False
        self.back_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.any_pressed = False
        self.fullscreen_pressed = False

        self._prev_keys: set[int] = set()
        self._keys: set[int] = set()
        self._just: set[int] = set()
        self._released: set[int] = set()

    def begin_frame(self) -> None:
        self.dash_pressed = False
        self.hit_pressed = False
        self.hit_released = False
        self.pause_pressed = False
        self.confirm_pressed = False
        self.back_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.any_pressed = False
        self.fullscreen_pressed = False
        self._just.clear()
        self._released.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._keys.add(event.key)
            self._just.add(event.key)
            self.any_pressed = True
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL):
                self.dash_pressed = True
            if event.key in (pygame.K_SPACE, pygame.K_z):
                self.hit_pressed = True
            if event.key == pygame.K_ESCAPE:
                self.pause_pressed = True
                self.back_pressed = True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirm_pressed = True
            if event.key in (pygame.K_UP, pygame.K_w):
                self.up_pressed = True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.down_pressed = True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.left_pressed = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.right_pressed = True
            if event.key == pygame.K_F11:
                self.fullscreen_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key in self._keys:
                self._keys.discard(event.key)
            self._released.add(event.key)
            if event.key in (pygame.K_SPACE, pygame.K_z):
                self.hit_released = True

    def end_frame(self) -> None:
        keys = pygame.key.get_pressed()
        mx = 0.0
        my = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            mx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            mx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            my -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            my += 1.0
        self.move_x, self.move_y = normalize(mx, my)
        self.hit_held = bool(keys[pygame.K_SPACE] or keys[pygame.K_z])
        self._prev_keys = set(self._keys)

    def key_down(self, key: int) -> bool:
        return key in self._keys

    def key_just(self, key: int) -> bool:
        return key in self._just
