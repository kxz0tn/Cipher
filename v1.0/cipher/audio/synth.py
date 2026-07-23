"""Low-level PCM synthesis primitives."""
from __future__ import annotations

import math
from typing import Callable

import numpy as np

from cipher.constants import SAMPLE_RATE


def _time_array(duration: float) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * duration))
    return np.arange(n, dtype=np.float64) / SAMPLE_RATE


def envelope_adsr(
    t: np.ndarray,
    duration: float,
    attack: float = 0.01,
    decay: float = 0.05,
    sustain: float = 0.6,
    release: float = 0.08,
) -> np.ndarray:
    env = np.zeros_like(t)
    release_start = max(0.0, duration - release)
    for i, ti in enumerate(t):
        if ti < attack:
            env[i] = ti / max(attack, 1e-6)
        elif ti < attack + decay:
            env[i] = 1.0 - (1.0 - sustain) * ((ti - attack) / max(decay, 1e-6))
        elif ti < release_start:
            env[i] = sustain
        else:
            env[i] = sustain * (1.0 - (ti - release_start) / max(release, 1e-6))
    return np.clip(env, 0.0, 1.0)


def osc_square(t: np.ndarray, freq: float) -> np.ndarray:
    return np.sign(np.sin(2 * math.pi * freq * t))


def osc_triangle(t: np.ndarray, freq: float) -> np.ndarray:
    return 2.0 * np.abs(2.0 * (t * freq - np.floor(t * freq + 0.5))) - 1.0


def osc_saw(t: np.ndarray, freq: float) -> np.ndarray:
    return 2.0 * (t * freq - np.floor(t * freq + 0.5))


def osc_noise(t: np.ndarray, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, size=t.shape)


def tone(
    freq: float,
    duration: float,
    wave: str = "square",
    volume: float = 0.4,
    attack: float = 0.01,
    decay: float = 0.05,
    sustain: float = 0.5,
    release: float = 0.06,
    slide_to: float | None = None,
) -> np.ndarray:
    t = _time_array(duration)
    if slide_to is not None and len(t):
        freqs = np.linspace(freq, slide_to, len(t))
        # integrate phase
        phase = np.cumsum(2 * math.pi * freqs / SAMPLE_RATE)
        if wave == "square":
            raw = np.sign(np.sin(phase))
        elif wave == "triangle":
            raw = 2.0 * np.abs(2.0 * (phase / (2 * math.pi) - np.floor(phase / (2 * math.pi) + 0.5))) - 1.0
        elif wave == "saw":
            raw = 2.0 * (phase / (2 * math.pi) - np.floor(phase / (2 * math.pi) + 0.5))
        else:
            raw = np.sin(phase)
    else:
        if wave == "square":
            raw = osc_square(t, freq)
        elif wave == "triangle":
            raw = osc_triangle(t, freq)
        elif wave == "saw":
            raw = osc_saw(t, freq)
        elif wave == "noise":
            raw = osc_noise(t, seed=int(freq))
        else:
            raw = np.sin(2 * math.pi * freq * t)
    env = envelope_adsr(t, duration, attack, decay, sustain, release)
    return (raw * env * volume).astype(np.float64)


def mix(*clips: np.ndarray) -> np.ndarray:
    if not clips:
        return np.zeros(1, dtype=np.float64)
    length = max(len(c) for c in clips)
    out = np.zeros(length, dtype=np.float64)
    for c in clips:
        out[: len(c)] += c
    peak = np.max(np.abs(out)) if len(out) else 1.0
    if peak > 1.0:
        out /= peak
    return out


def to_sound(samples: np.ndarray):
    """Convert mono float samples to a pygame Sound."""
    import pygame

    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    # stereo
    stereo = np.column_stack([pcm, pcm])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


def note_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))
