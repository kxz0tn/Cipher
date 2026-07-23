"""Match scoring, countdown clock, and phase state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from cipher.constants import COUNTDOWN_SECONDS, GOAL_FREEZE_SECONDS, GOALS_TO_WIN


class MatchPhase(Enum):
    COUNTDOWN = auto()
    PLAYING = auto()
    GOAL = auto()
    OVER = auto()


@dataclass
class MatchState:
    player_score: int = 0
    enemy_score: int = 0
    goals_to_win: int = GOALS_TO_WIN
    phase: MatchPhase = MatchPhase.COUNTDOWN
    phase_timer: float = COUNTDOWN_SECONDS
    match_time: float = 0.0  # elapsed seconds (for scoring)
    time_remaining: float = 180.0  # countdown display / end
    match_duration: float = 180.0
    last_scorer: str | None = None  # "player" | "enemy"
    winner: str | None = None
    countdown_value: int = 3
    time_expired: bool = False

    def configure_duration(self, seconds: float) -> None:
        self.match_duration = float(seconds)
        self.time_remaining = float(seconds)
        self.match_time = 0.0
        self.time_expired = False

    def reset_round(self) -> None:
        self.phase = MatchPhase.COUNTDOWN
        self.phase_timer = COUNTDOWN_SECONDS
        self.countdown_value = 3
        self.last_scorer = None

    def score(self, who: str) -> None:
        if who == "player":
            self.player_score += 1
        else:
            self.enemy_score += 1
        self.last_scorer = who
        self.phase = MatchPhase.GOAL
        self.phase_timer = GOAL_FREEZE_SECONDS
        if self.player_score >= self.goals_to_win:
            self.winner = "player"
        elif self.enemy_score >= self.goals_to_win:
            self.winner = "enemy"

    def end_by_time(self) -> None:
        """Resolve match when countdown hits zero."""
        self.time_remaining = 0.0
        self.time_expired = True
        if self.player_score > self.enemy_score:
            self.winner = "player"
        elif self.enemy_score > self.player_score:
            self.winner = "enemy"
        else:
            # True draw at buzzer — no winner
            self.winner = None
        self.phase = MatchPhase.OVER

    def update_phase(self, dt: float) -> list[str]:
        """Advance timers; return event tags."""
        events: list[str] = []
        if self.phase == MatchPhase.OVER:
            return events

        if self.phase == MatchPhase.PLAYING:
            self.match_time += dt
            self.time_remaining = max(0.0, self.time_remaining - dt)
            if self.time_remaining <= 0.0 and not self.time_expired:
                self.end_by_time()
                events.append("time_up")
                events.append("match_over")
            return events

        self.phase_timer -= dt
        if self.phase == MatchPhase.COUNTDOWN:
            new_val = max(0, int(math_ceil(self.phase_timer)))
            if new_val != self.countdown_value and self.phase_timer > 0:
                self.countdown_value = new_val
                events.append("countdown_tick")
            if self.phase_timer <= 0:
                self.phase = MatchPhase.PLAYING
                events.append("go")
        elif self.phase == MatchPhase.GOAL:
            if self.phase_timer <= 0:
                if self.winner:
                    self.phase = MatchPhase.OVER
                    events.append("match_over")
                else:
                    self.reset_round()
                    events.append("reset_round")
        return events


def math_ceil(x: float) -> int:
    import math

    return int(math.ceil(x))
