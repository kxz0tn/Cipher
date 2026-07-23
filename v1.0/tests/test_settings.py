"""Settings / highscore pure logic tests."""
from cipher.highscores import ScoreEntry, compute_points, qualifies
from cipher.settings import Settings


def test_settings_clamp() -> None:
    s = Settings(master_volume=2.0, music_volume=-1.0)
    s.clamp()
    assert s.master_volume == 1.0
    assert s.music_volume == 0.0


def test_compute_points_win() -> None:
    pts = compute_points(5, 2, "Operative", True, 60.0)
    assert pts > 0


def test_qualifies_empty() -> None:
    assert qualifies(100, [])


def test_qualifies_full_table() -> None:
    scores = [
        ScoreEntry("AAA", 1000 - i * 10, "Quick", "Neon", "Operative", 5, 2, "2026-01-01")
        for i in range(10)
    ]
    assert not qualifies(1, scores)
    assert qualifies(9999, scores)
