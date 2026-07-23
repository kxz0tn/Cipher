"""Player entity (Vex and opponent body)."""
from __future__ import annotations

from dataclasses import dataclass, field

from cipher.constants import (
    CYAN,
    MAGENTA,
    PLAYER_ACCEL,
    PLAYER_CHARGE_FORCE_MAX,
    PLAYER_CHARGE_FORCE_MIN,
    PLAYER_CHARGE_MAX,
    PLAYER_CHARGE_RATE,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_SPEED,
    PLAYER_DASH_TIME,
    PLAYER_FRICTION,
    PLAYER_INFLUENCE_RADIUS,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
)
from cipher.core.math_util import clamp, length, normalize
from cipher.gameplay.physics import apply_friction, clamp_speed, integrate
from cipher.render.fx import Trail


@dataclass
class Player:
    x: float
    y: float
    team: str = "vex"  # vex | foe
    vx: float = 0.0
    vy: float = 0.0
    radius: float = PLAYER_RADIUS
    facing_x: float = 1.0
    facing_y: float = 0.0
    dash_timer: float = 0.0
    dash_cd: float = 0.0
    charge: float = 0.0
    charging: bool = False
    speed_mul: float = 1.0
    shield: bool = False
    shield_time: float = 0.0
    overdrive: bool = False
    overdrive_time: float = 0.0
    speed_time: float = 0.0
    invuln: float = 0.0
    trail: Trail = field(default_factory=lambda: Trail(10))
    frame: int = 0
    name: str = "VEX"

    @property
    def color(self) -> tuple[int, int, int]:
        return CYAN if self.team == "vex" else MAGENTA

    @property
    def influence(self) -> float:
        return PLAYER_INFLUENCE_RADIUS * (1.15 if self.overdrive else 1.0)

    def apply_input(self, mx: float, my: float, dash: bool, hit_held: bool, dt: float) -> None:
        max_spd = PLAYER_MAX_SPEED * self.speed_mul * (1.25 if self.overdrive else 1.0)
        accel = PLAYER_ACCEL * self.speed_mul

        if self.dash_timer > 0:
            # dash locks velocity
            pass
        else:
            if mx or my:
                self.vx += mx * accel * dt
                self.vy += my * accel * dt
                self.facing_x, self.facing_y = normalize(mx, my)
            else:
                self.vx, self.vy = apply_friction(self.vx, self.vy, PLAYER_FRICTION, dt)

            self.vx, self.vy = clamp_speed(self.vx, self.vy, max_spd)

        if dash and self.dash_cd <= 0 and self.dash_timer <= 0:
            fx, fy = self.facing_x, self.facing_y
            if abs(mx) + abs(my) > 0.1:
                fx, fy = normalize(mx, my)
            if abs(fx) + abs(fy) < 0.1:
                fx, fy = (1.0 if self.team == "vex" else -1.0), 0.0
            self.facing_x, self.facing_y = fx, fy
            dash_spd = PLAYER_DASH_SPEED * self.speed_mul
            self.vx = fx * dash_spd
            self.vy = fy * dash_spd
            self.dash_timer = PLAYER_DASH_TIME
            self.dash_cd = PLAYER_DASH_COOLDOWN
            self.invuln = PLAYER_DASH_TIME
            return  # caller plays sfx

        if hit_held:
            self.charging = True
            self.charge = clamp(self.charge + PLAYER_CHARGE_RATE * dt, 0.0, PLAYER_CHARGE_MAX)
        else:
            self.charging = False

    def release_shot_force(self) -> float:
        t = self.charge
        self.charge = 0.0
        self.charging = False
        if t < 0.08:
            return PLAYER_CHARGE_FORCE_MIN * 0.55
        return PLAYER_CHARGE_FORCE_MIN + (PLAYER_CHARGE_FORCE_MAX - PLAYER_CHARGE_FORCE_MIN) * t

    def update_timers(self, dt: float) -> None:
        if self.dash_timer > 0:
            self.dash_timer = max(0.0, self.dash_timer - dt)
        if self.dash_cd > 0:
            self.dash_cd = max(0.0, self.dash_cd - dt)
        if self.invuln > 0:
            self.invuln = max(0.0, self.invuln - dt)
        if self.speed_time > 0:
            self.speed_time = max(0.0, self.speed_time - dt)
            if self.speed_time <= 0:
                self.speed_mul = 1.0
        if self.shield_time > 0:
            self.shield_time = max(0.0, self.shield_time - dt)
            if self.shield_time <= 0:
                self.shield = False
        if self.overdrive_time > 0:
            self.overdrive_time = max(0.0, self.overdrive_time - dt)
            if self.overdrive_time <= 0:
                self.overdrive = False
        self.frame += 1

    def integrate(self, dt: float) -> None:
        self.x, self.y = integrate(self.x, self.y, self.vx, self.vy, dt)
        self.trail.add(self.x, self.y)
        self.trail.update(dt)

    def give_speed(self, duration: float, mul: float = 1.45) -> None:
        self.speed_mul = mul
        self.speed_time = duration

    def give_shield(self, duration: float) -> None:
        self.shield = True
        self.shield_time = duration

    def give_overdrive(self, duration: float) -> None:
        self.overdrive = True
        self.overdrive_time = duration
        self.speed_mul = max(self.speed_mul, 1.2)

    def consume_shield(self) -> bool:
        if self.shield:
            self.shield = False
            self.shield_time = 0.0
            return True
        return False
