"""Scene base class and stack helpers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import pygame

if TYPE_CHECKING:
    from cipher.app import App


class Scene(ABC):
    def __init__(self, app: App) -> None:
        self.app = app

    def enter(self, **kwargs: Any) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def fixed_update(self, dt: float) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass
