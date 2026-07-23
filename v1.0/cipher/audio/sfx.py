"""One-shot SFX bank — fully procedural."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from cipher.audio.synth import mix, note_freq, to_sound, tone

if TYPE_CHECKING:
    from cipher.settings import Settings


class SFXBank:
    def __init__(self) -> None:
        self._sounds: dict[str, object] = {}
        self._settings: Settings | None = None
        self._built = False

    def bind_settings(self, settings: Settings) -> None:
        self._settings = settings

    def build(self) -> None:
        if self._built:
            return
        self._sounds = {
            "blip": to_sound(tone(note_freq(76), 0.05, "square", 0.35, 0.005, 0.02, 0.3, 0.03)),
            "confirm": to_sound(
                mix(
                    tone(note_freq(72), 0.08, "square", 0.3),
                    tone(note_freq(79), 0.1, "square", 0.25, 0.01, 0.03, 0.4, 0.05),
                )
            ),
            "back": to_sound(tone(note_freq(64), 0.07, "triangle", 0.3, slide_to=note_freq(60))),
            "dash": to_sound(
                mix(
                    tone(220, 0.08, "saw", 0.25, slide_to=480),
                    tone(0, 0.06, "noise", 0.15, 0.001, 0.02, 0.2, 0.03),
                )
            ),
            "charge": to_sound(tone(180, 0.06, "triangle", 0.2, slide_to=320)),
            "launch": to_sound(
                mix(
                    tone(300, 0.12, "square", 0.35, slide_to=120),
                    tone(0, 0.08, "noise", 0.2),
                )
            ),
            "bounce": to_sound(tone(note_freq(67), 0.05, "triangle", 0.28, 0.001, 0.02, 0.2, 0.03)),
            "wall": to_sound(tone(140, 0.04, "square", 0.2)),
            "goal": to_sound(
                mix(
                    tone(note_freq(72), 0.12, "square", 0.35),
                    tone(note_freq(76), 0.14, "square", 0.3),
                    tone(note_freq(79), 0.18, "square", 0.28),
                    tone(note_freq(84), 0.22, "triangle", 0.25),
                )
            ),
            "powerup_spawn": to_sound(
                mix(
                    tone(note_freq(71), 0.08, "triangle", 0.25),
                    tone(note_freq(78), 0.1, "triangle", 0.2),
                )
            ),
            "powerup": to_sound(
                mix(
                    tone(note_freq(74), 0.1, "square", 0.3),
                    tone(note_freq(81), 0.12, "square", 0.25),
                )
            ),
            "countdown": to_sound(tone(note_freq(69), 0.1, "square", 0.35)),
            "go": to_sound(
                mix(
                    tone(note_freq(76), 0.1, "square", 0.35),
                    tone(note_freq(83), 0.15, "square", 0.3),
                )
            ),
            "win": to_sound(
                mix(
                    tone(note_freq(72), 0.12, "square", 0.3),
                    tone(note_freq(76), 0.12, "square", 0.28),
                    tone(note_freq(79), 0.14, "square", 0.28),
                    tone(note_freq(84), 0.25, "triangle", 0.3),
                )
            ),
            "lose": to_sound(
                mix(
                    tone(note_freq(67), 0.15, "saw", 0.28, slide_to=note_freq(60)),
                    tone(note_freq(63), 0.2, "triangle", 0.22, slide_to=note_freq(55)),
                )
            ),
            "hit": to_sound(
                mix(
                    tone(200, 0.05, "square", 0.25),
                    tone(0, 0.04, "noise", 0.18),
                )
            ),
        }
        self._built = True

    def play(self, name: str, volume_scale: float = 1.0) -> None:
        if not self._built:
            self.build()
        snd = self._sounds.get(name)
        if snd is None:
            return
        vol = volume_scale
        if self._settings is not None:
            vol *= self._settings.effective_sfx()
        snd.set_volume(max(0.0, min(1.0, vol)))
        snd.play()

    def stop_all(self) -> None:
        for snd in self._sounds.values():
            try:
                snd.stop()
            except Exception:
                pass


# module singleton used by app
SFX = SFXBank()
