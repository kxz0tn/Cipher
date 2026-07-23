"""Difficulty-scaled opponent brain."""
from __future__ import annotations

import math
import random

from cipher.constants import DIFFICULTY_PROFILES, PLAYER_INFLUENCE_RADIUS
from cipher.core.math_util import dist, normalize


class AIController:
    def __init__(self, difficulty: str = "Operative") -> None:
        profile = DIFFICULTY_PROFILES.get(difficulty, DIFFICULTY_PROFILES["Operative"])
        self.reaction = float(profile["ai_reaction"])
        self.aim_error = float(profile["ai_aim_error"])
        self.aggression = float(profile["ai_aggression"])
        self.dash_chance = float(profile["ai_dash_chance"])
        self._think_timer = 0.0
        self._mx = 0.0
        self._my = 0.0
        self._dash = False
        self._hit = False
        self._target_x = 0.0
        self._target_y = 0.0

    def update(
        self,
        dt: float,
        me,
        ball,
        own_goal_x: float,
        own_goal_y: float,
        enemy_goal_x: float,
        enemy_goal_y: float,
        arena_bounds: tuple[float, float, float, float],
    ) -> tuple[float, float, bool, bool]:
        """Returns move_x, move_y, dash_pressed, hit_held."""
        self._dash = False
        self._think_timer -= dt
        if self._think_timer <= 0:
            self._think_timer = self.reaction * random.uniform(0.7, 1.3)
            self._rethink(me, ball, own_goal_x, own_goal_y, enemy_goal_x, enemy_goal_y)

        # charge when near ball and aiming at goal
        near = dist(me.x, me.y, ball.x, ball.y) < PLAYER_INFLUENCE_RADIUS * 1.3
        self._hit = near and self._should_shoot(me, ball, enemy_goal_x, enemy_goal_y)

        # occasional dash toward target
        if near and random.random() < self.dash_chance * dt * 2:
            self._dash = True
        elif dist(me.x, me.y, self._target_x, self._target_y) > 180 and random.random() < self.dash_chance * dt:
            self._dash = True

        dx = self._target_x - me.x
        dy = self._target_y - me.y
        self._mx, self._my = normalize(dx, dy)

        # jitter
        if self.aim_error > 0:
            self._mx += random.uniform(-self.aim_error, self.aim_error) * 0.35
            self._my += random.uniform(-self.aim_error, self.aim_error) * 0.35
            self._mx, self._my = normalize(self._mx, self._my)

        return self._mx, self._my, self._dash, self._hit

    def _rethink(self, me, ball, own_gx, own_gy, enemy_gx, enemy_gy) -> None:
        # Predict ball a bit
        pred_t = 0.15 + (1.0 - self.aggression) * 0.25
        bx = ball.x + ball.vx * pred_t
        by = ball.y + ball.vy * pred_t

        # If ball is closer to our goal, defend
        dist_own = abs(bx - own_gx)
        dist_enemy = abs(bx - enemy_gx)
        ball_threat = dist_own < dist_enemy * (1.1 - self.aggression * 0.3)

        if ball_threat and self.aggression < 0.9:
            # intercept between ball and own goal
            self._target_x = (bx + own_gx) * 0.5
            self._target_y = (by + own_gy) * 0.5
            # bias toward ball
            self._target_x = self._target_x * 0.4 + bx * 0.6
            self._target_y = self._target_y * 0.4 + by * 0.6
        else:
            # attack: get behind ball relative to enemy goal
            dx = enemy_gx - bx
            dy = enemy_gy - by
            nx, ny = normalize(dx, dy)
            # approach from opposite side of goal direction
            self._target_x = bx - nx * 28
            self._target_y = by - ny * 10 + random.uniform(-20, 20) * self.aim_error

        # keep AI in its half bias slightly when low aggression
        if self.aggression < 0.5:
            mid = (own_gx + enemy_gx) * 0.5
            if me.team == "foe":
                self._target_x = max(self._target_x, mid - 40)
            else:
                self._target_x = min(self._target_x, mid + 40)

    def _should_shoot(self, me, ball, enemy_gx, enemy_gy) -> bool:
        # Face-ish toward enemy goal
        to_goal_x = enemy_gx - me.x
        to_ball_x = ball.x - me.x
        # if ball is between us and goal (roughly)
        if me.team == "foe":
            good = ball.x < me.x - 5  # ball left of foe (toward left goal)
        else:
            good = ball.x > me.x + 5
        # charge longer at higher aggression
        return good or random.random() < self.aggression * 0.4
