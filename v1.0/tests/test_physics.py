"""Physics unit tests."""
from cipher.core.math_util import clamp, normalize, reflect
from cipher.gameplay.physics import clamp_speed, resolve_circle_circle, resolve_circle_rect_bounds


def test_clamp() -> None:
    assert clamp(5, 0, 3) == 3
    assert clamp(-1, 0, 3) == 0
    assert clamp(1, 0, 3) == 1


def test_normalize() -> None:
    x, y = normalize(3, 0)
    assert abs(x - 1) < 1e-6 and abs(y) < 1e-6


def test_reflect() -> None:
    vx, vy = reflect(1, -1, 0, 1)
    assert abs(vx - 1) < 1e-6 and abs(vy - 1) < 1e-6


def test_clamp_speed() -> None:
    vx, vy = clamp_speed(100, 0, 50)
    assert abs(vx - 50) < 1e-6


def test_wall_bounce() -> None:
    x, y, vx, vy, hit, side = resolve_circle_rect_bounds(
        5, 50, -10, 0, 10, 0, 0, 200, 200, restitution=1.0
    )
    assert hit and side == "left"
    assert vx > 0


def test_circle_collision_separates() -> None:
    ax, ay, avx, avy, bx, by, bvx, bvy, hit = resolve_circle_circle(
        0, 0, 10, 0, 10, 1.0,
        15, 0, -10, 0, 10, 1.0,
        restitution=1.0,
    )
    assert hit
    assert bx - ax >= 19.5
