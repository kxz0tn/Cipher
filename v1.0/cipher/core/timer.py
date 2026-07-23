"""Fixed timestep accumulator."""
from __future__ import annotations

from cipher.constants import FIXED_DT, MAX_FRAME_CATCHUP


class FixedTimer:
    def __init__(self, dt: float = FIXED_DT, max_steps: int = MAX_FRAME_CATCHUP) -> None:
        self.dt = dt
        self.max_steps = max_steps
        self.accumulator = 0.0

    def consume(self, frame_dt: float) -> int:
        """Add frame time and return number of fixed steps to run."""
        # Cap single frame contribution to avoid spiral of death
        frame_dt = min(frame_dt, self.dt * self.max_steps)
        self.accumulator += frame_dt
        steps = 0
        while self.accumulator >= self.dt and steps < self.max_steps:
            self.accumulator -= self.dt
            steps += 1
        # Drop leftover if we hit cap
        if steps >= self.max_steps:
            self.accumulator = 0.0
        return steps

    @property
    def alpha(self) -> float:
        return self.accumulator / self.dt if self.dt > 0 else 0.0
