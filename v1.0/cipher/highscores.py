"""Local high-score table."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cipher.settings import user_data_dir

MAX_SCORES = 10


@dataclass
class ScoreEntry:
    name: str
    points: int
    mode: str
    arena: str
    difficulty: str
    goals_for: int
    goals_against: int
    date: str

    def sort_key(self) -> tuple:
        return (self.points, self.goals_for - self.goals_against, self.date)


def _path() -> Path:
    return user_data_dir() / "highscores.json"


def load_scores() -> list[ScoreEntry]:
    path = _path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return []
        out: list[ScoreEntry] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            out.append(
                ScoreEntry(
                    name=str(item.get("name", "VEX"))[:3].upper(),
                    points=int(item.get("points", 0)),
                    mode=str(item.get("mode", "Quick")),
                    arena=str(item.get("arena", "")),
                    difficulty=str(item.get("difficulty", "")),
                    goals_for=int(item.get("goals_for", 0)),
                    goals_against=int(item.get("goals_against", 0)),
                    date=str(item.get("date", "")),
                )
            )
        out.sort(key=lambda e: e.sort_key(), reverse=True)
        return out[:MAX_SCORES]
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []


def save_scores(scores: list[ScoreEntry]) -> None:
    scores = sorted(scores, key=lambda e: e.sort_key(), reverse=True)[:MAX_SCORES]
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data: list[dict[str, Any]] = [asdict(s) for s in scores]
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def clear_scores() -> None:
    """Wipe the high-score table completely."""
    save_scores([])


def qualifies(
    points: int,
    scores: list[ScoreEntry] | None = None,
    *,
    won: bool = True,
) -> bool:
    """High scores only on wins. Loss / draw never qualify."""
    if not won or points <= 0:
        return False
    scores = scores if scores is not None else load_scores()
    if len(scores) < MAX_SCORES:
        return True
    return points > scores[-1].points


def normalize_name(name: str) -> str:
    """Canonical 3-letter high-score name."""
    return name[:3].upper().ljust(3, "A")


def name_exists(name: str, scores: list[ScoreEntry] | None = None) -> bool:
    """True if this name is already on the high-score table."""
    key = normalize_name(name)
    scores = scores if scores is not None else load_scores()
    return any(s.name == key for s in scores)


def insert_score(
    entry: ScoreEntry,
    scores: list[ScoreEntry] | None = None,
    *,
    won: bool = True,
) -> list[ScoreEntry] | None:
    """Insert score only on win + unique name. Returns None if rejected."""
    if not won:
        return None
    scores = list(scores if scores is not None else load_scores())
    entry.name = normalize_name(entry.name)
    if name_exists(entry.name, scores):
        return None
    scores.append(entry)
    scores.sort(key=lambda e: e.sort_key(), reverse=True)
    scores = scores[:MAX_SCORES]
    save_scores(scores)
    return scores


def make_entry(
    name: str,
    points: int,
    mode: str,
    arena: str,
    difficulty: str,
    goals_for: int,
    goals_against: int,
) -> ScoreEntry:
    return ScoreEntry(
        name=normalize_name(name),
        points=int(points),
        mode=mode,
        arena=arena,
        difficulty=difficulty,
        goals_for=goals_for,
        goals_against=goals_against,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


def compute_points(
    goals_for: int,
    goals_against: int,
    difficulty: str,
    won: bool,
    match_seconds: float,
) -> int:
    from cipher.constants import DIFFICULTY_PROFILES

    mul = DIFFICULTY_PROFILES.get(difficulty, {}).get("score_mul", 1.0)
    base = goals_for * 100 - goals_against * 40
    if won:
        base += 250
        # faster wins slightly better
        base += max(0, int(120 - match_seconds * 0.15))
    base = max(0, int(base * mul))
    return base
