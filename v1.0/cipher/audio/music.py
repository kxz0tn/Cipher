"""Looping procedural chiptune music by scene mood."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from cipher.audio.synth import mix, note_freq, to_sound, tone
from cipher.constants import SAMPLE_RATE

if TYPE_CHECKING:
    from cipher.settings import Settings


def _pattern_loop(
    notes: list[tuple[int | None, float]],
    wave: str = "square",
    volume: float = 0.18,
    bpm: float = 120.0,
) -> np.ndarray:
    """notes: list of (midi or None for rest, beats)."""
    beat = 60.0 / bpm
    clips: list[np.ndarray] = []
    cursor = 0.0
    parts: list[tuple[int, np.ndarray]] = []
    for midi, beats in notes:
        dur = beat * beats
        if midi is not None:
            clip = tone(note_freq(midi), dur * 0.95, wave, volume, 0.005, 0.03, 0.4, 0.05)
            parts.append((int(cursor * SAMPLE_RATE), clip))
        cursor += dur
    total = max(1, int(cursor * SAMPLE_RATE))
    out = np.zeros(total, dtype=np.float64)
    for start, clip in parts:
        end = min(total, start + len(clip))
        out[start:end] += clip[: end - start]
    peak = np.max(np.abs(out)) if len(out) else 1.0
    if peak > 0.9:
        out *= 0.9 / peak
    return out


def _bass_line(bpm: float = 120.0) -> np.ndarray:
    notes = [
        (36, 1),
        (36, 1),
        (39, 1),
        (36, 1),
        (41, 1),
        (39, 1),
        (36, 1),
        (34, 1),
    ]
    return _pattern_loop(notes, "triangle", 0.22, bpm)


def _menu_melody(bpm: float = 100.0) -> np.ndarray:
    notes = [
        (60, 0.5),
        (63, 0.5),
        (67, 0.5),
        (63, 0.5),
        (60, 0.5),
        (58, 0.5),
        (55, 1.0),
        (58, 0.5),
        (60, 0.5),
        (63, 0.5),
        (67, 0.5),
        (70, 0.5),
        (67, 0.5),
        (63, 1.0),
    ]
    return _pattern_loop(notes, "square", 0.14, bpm)


def _match_melody(bpm: float = 140.0) -> np.ndarray:
    notes = [
        (67, 0.25),
        (70, 0.25),
        (72, 0.25),
        (70, 0.25),
        (67, 0.25),
        (65, 0.25),
        (67, 0.5),
        (72, 0.25),
        (75, 0.25),
        (72, 0.25),
        (70, 0.25),
        (67, 0.5),
        (None, 0.25),
        (65, 0.25),
        (67, 0.5),
        (70, 0.25),
        (72, 0.25),
        (75, 0.5),
        (72, 0.5),
    ]
    return _pattern_loop(notes, "square", 0.13, bpm)


def _arp(bpm: float = 140.0) -> np.ndarray:
    notes = []
    for _ in range(4):
        for m in (60, 63, 67, 72):
            notes.append((m, 0.25))
    return _pattern_loop(notes, "triangle", 0.08, bpm)


class MusicPlayer:
    def __init__(self) -> None:
        self._settings: Settings | None = None
        self._current: str | None = None
        self._sound = None
        self._channel = None
        self._cache: dict[str, object] = {}

    def bind_settings(self, settings: Settings) -> None:
        self._settings = settings
        self._apply_volume()

    def _build(self, name: str):
        if name in self._cache:
            return self._cache[name]
        if name == "menu":
            samples = mix(_bass_line(100), _menu_melody(100), _arp(100) * 0.6)
        elif name == "match":
            samples = mix(_bass_line(140), _match_melody(140), _arp(140))
        elif name == "title":
            samples = mix(_bass_line(90), _menu_melody(90))
        else:
            samples = _bass_line(110)
        snd = to_sound(samples)
        self._cache[name] = snd
        return snd

    def _apply_volume(self) -> None:
        if self._sound is None:
            return
        vol = 0.5
        if self._settings is not None:
            vol = self._settings.effective_music()
        self._sound.set_volume(max(0.0, min(1.0, vol)))

    def play(self, name: str, loops: int = -1) -> None:
        if self._current == name and self._channel is not None and self._channel.get_busy():
            self._apply_volume()
            return
        # Never use fadeout when switching — leaves channels half-alive on exit races
        self.stop(fade_ms=0)
        self._sound = self._build(name)
        self._apply_volume()
        # Dedicated channel 0 for music so we can always kill it by index
        import pygame

        try:
            ch = pygame.mixer.Channel(0)
            ch.stop()
            ch.play(self._sound, loops=loops)
            self._channel = ch
        except Exception:
            self._channel = self._sound.play(loops=loops)
        self._current = name

    def stop(self, fade_ms: int = 0) -> None:
        """Stop current track immediately. fade_ms is ignored (always hard stop)."""
        # Kill channel 0 (music) and any tracked channel
        try:
            import pygame

            if pygame.mixer.get_init() is not None:
                try:
                    pygame.mixer.Channel(0).stop()
                except Exception:
                    pass
                if self._channel is not None:
                    try:
                        self._channel.stop()
                    except Exception:
                        pass
                for snd in list(self._cache.values()):
                    try:
                        snd.stop()
                    except Exception:
                        pass
        except Exception:
            pass
        self._channel = None
        self._current = None
        self._sound = None

    def hard_stop(self) -> None:
        """Immediate full silence — used on application exit."""
        self.stop(fade_ms=0)
        # Drop references so GC can free PCM buffers
        self._cache.clear()


    def update_volume(self) -> None:
        self._apply_volume()


MUSIC = MusicPlayer()
