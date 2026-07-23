"""Collision and integration helpers — robust separation, no sticking/tunneling."""
from __future__ import annotations

import math

from cipher.core.math_util import dot, length


def integrate(x: float, y: float, vx: float, vy: float, dt: float) -> tuple[float, float]:
    return x + vx * dt, y + vy * dt


def apply_friction(vx: float, vy: float, friction: float, dt: float) -> tuple[float, float]:
    speed = length(vx, vy)
    if speed < 1e-6:
        return 0.0, 0.0
    new_speed = max(0.0, speed - friction * dt)
    scale = new_speed / speed
    return vx * scale, vy * scale


def clamp_speed(vx: float, vy: float, max_speed: float) -> tuple[float, float]:
    speed = length(vx, vy)
    if speed > max_speed:
        s = max_speed / speed
        return vx * s, vy * s
    return vx, vy


def resolve_circle_circle(
    ax: float,
    ay: float,
    avx: float,
    avy: float,
    ar: float,
    am: float,
    bx: float,
    by: float,
    bvx: float,
    bvy: float,
    br: float,
    bm: float,
    restitution: float = 0.9,
    sep_slop: float = 0.5,
) -> tuple[float, float, float, float, float, float, float, float, bool]:
    """Solid circle-circle. Always separates overlap; applies bounce impulse."""
    dx = bx - ax
    dy = by - ay
    dist = math.hypot(dx, dy)
    min_dist = ar + br

    if dist >= min_dist:
        return ax, ay, avx, avy, bx, by, bvx, bvy, False

    # Degenerate center overlap — pick a stable normal
    if dist < 1e-6:
        nx, ny = 1.0, 0.0
        dist = 1e-6
    else:
        nx, ny = dx / dist, dy / dist

    inv_a = 0.0 if am <= 0 else 1.0 / am
    inv_b = 0.0 if bm <= 0 else 1.0 / bm
    inv_sum = inv_a + inv_b
    if inv_sum <= 0:
        return ax, ay, avx, avy, bx, by, bvx, bvy, False

    # Positional correction — fully clear overlap + small slop so they don't re-stick
    overlap = (min_dist - dist) + sep_slop
    corr = overlap / inv_sum
    ax -= nx * corr * inv_a
    ay -= ny * corr * inv_a
    bx += nx * corr * inv_b
    by += ny * corr * inv_b

    # Relative velocity along normal
    rvx = bvx - avx
    rvy = bvy - avy
    vel_along_normal = dot(rvx, rvy, nx, ny)

    # If separating already, still count as hit (positions fixed)
    if vel_along_normal > 0:
        return ax, ay, avx, avy, bx, by, bvx, bvy, True

    # Bounce impulse
    e = restitution
    j = -(1.0 + e) * vel_along_normal
    j /= inv_sum
    # Minimum kick so slow crawls still bounce apart
    j = max(j, 40.0 * (am + bm) * 0.5)

    ix, iy = j * nx, j * ny
    avx -= ix * inv_a
    avy -= iy * inv_a
    bvx += ix * inv_b
    bvy += iy * inv_b
    return ax, ay, avx, avy, bx, by, bvx, bvy, True


def resolve_circle_rect_bounds(
    x: float,
    y: float,
    vx: float,
    vy: float,
    radius: float,
    left: float,
    top: float,
    right: float,
    bottom: float,
    restitution: float = 0.9,
    skip_left_goal: tuple[float, float] | None = None,
    skip_right_goal: tuple[float, float] | None = None,
    friction_tangent: float = 0.15,
) -> tuple[float, float, float, float, bool, str | None]:
    """
    Keep circle inside AABB. Never leaves body embedded in wall.
    Always kills inward velocity and re-clamps after multi-axis hits (corners).
    """
    hit = False
    side = None
    eps = 0.75  # keep slightly inside so next frame doesn't re-penetrate

    def in_goal_y(gy: tuple[float, float] | None) -> bool:
        if gy is None:
            return False
        cy, hh = gy
        return (cy - hh) <= y <= (cy + hh)

    # Resolve X
    if x - radius < left and not in_goal_y(skip_left_goal):
        x = left + radius + eps
        if vx < 0:
            vx = -vx * restitution
        # kill residual inward
        if vx < 0:
            vx = 0.0
        vy *= 1.0 - friction_tangent
        hit = True
        side = "left"
    elif x + radius > right and not in_goal_y(skip_right_goal):
        x = right - radius - eps
        if vx > 0:
            vx = -vx * restitution
        if vx > 0:
            vx = 0.0
        vy *= 1.0 - friction_tangent
        hit = True
        side = "right"

    # Resolve Y
    if y - radius < top:
        y = top + radius + eps
        if vy < 0:
            vy = -vy * restitution
        if vy < 0:
            vy = 0.0
        vx *= 1.0 - friction_tangent
        hit = True
        side = "top"
    elif y + radius > bottom:
        y = bottom - radius - eps
        if vy > 0:
            vy = -vy * restitution
        if vy > 0:
            vy = 0.0
        vx *= 1.0 - friction_tangent
        hit = True
        side = "bottom"

    # Final hard clamp (corners / float error) — never leave inside wall
    x = max(left + radius + eps, min(right - radius - eps, x))
    y = max(top + radius + eps, min(bottom - radius - eps, y))

    # If still somehow outside (goal gaps), only clamp y fully
    # For goal mouths, allow x slightly outside bound later via skip — re-check:
    if not in_goal_y(skip_left_goal) and x - radius < left:
        x = left + radius + eps
        if vx < 0:
            vx = abs(vx) * restitution
    if not in_goal_y(skip_right_goal) and x + radius > right:
        x = right - radius - eps
        if vx > 0:
            vx = -abs(vx) * restitution

    return x, y, vx, vy, hit, side


def clamp_entity_in_bounds(
    x: float,
    y: float,
    radius: float,
    left: float,
    top: float,
    right: float,
    bottom: float,
) -> tuple[float, float]:
    """Hard position-only clamp (post-collision safety)."""
    eps = 0.75
    x = max(left + radius + eps, min(right - radius - eps, x))
    y = max(top + radius + eps, min(bottom - radius - eps, y))
    return x, y


def kill_inward_velocity_at_bounds(
    x: float,
    y: float,
    vx: float,
    vy: float,
    radius: float,
    left: float,
    top: float,
    right: float,
    bottom: float,
) -> tuple[float, float]:
    """Zero velocity components that push into walls when sitting on a bound.

    Prevents re-embedding / stick after positional clamps.
    """
    eps = 0.75
    pad = 0.05
    if x <= left + radius + eps + pad and vx < 0:
        vx = 0.0
    if x >= right - radius - eps - pad and vx > 0:
        vx = 0.0
    if y <= top + radius + eps + pad and vy < 0:
        vy = 0.0
    if y >= bottom - radius - eps - pad and vy > 0:
        vy = 0.0
    return vx, vy


def circle_hits_circle(
    ax: float, ay: float, ar: float, bx: float, by: float, br: float
) -> bool:
    return (ax - bx) ** 2 + (ay - by) ** 2 <= (ar + br) ** 2
