"""Core match gameplay scene."""
from __future__ import annotations

import math
from typing import Any

import pygame

from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.constants import (
    AI_NAMES,
    ARENA_MATCH_SECONDS,
    ARENA_NAMES,
    BALL_FRICTION,
    BALL_MAX_SPEED,
    BALL_MASS,
    BALL_RESTITUTION,
    BALL_WALL_RESTITUTION,
    CYAN,
    DEFAULT_MATCH_SECONDS,
    DIFFICULTY_PROFILES,
    GOAL_HEIGHT,
    INTERNAL_H,
    INTERNAL_W,
    MAGENTA,
    PLAYER_HIT_FORCE,
    PLAYER_MAGNET_STRENGTH,
    PLAYER_MASS,
    PURPLE,
    WHITE_GLOW,
    YELLOW,
)
from cipher.core.camera import CameraFX
from cipher.core.math_util import dist, length as vec_length, normalize
from cipher.gameplay.ai import AIController
from cipher.gameplay.arena import create_arena
from cipher.gameplay.ball import Ball
from cipher.gameplay.match_state import MatchPhase, MatchState
from cipher.gameplay.physics import (
    apply_friction,
    clamp_entity_in_bounds,
    clamp_speed,
    kill_inward_velocity_at_bounds,
    resolve_circle_circle,
    resolve_circle_rect_bounds,
)
from cipher.gameplay.player import Player
from cipher.gameplay.powerups import PowerUpManager
from cipher.highscores import compute_points
from cipher.render.backgrounds import Starfield
from cipher.render.font import draw_text
from cipher.render.fx import ParticleSystem
from cipher.render.palette import with_alpha
from cipher.render.sprites import (
    make_ball_sprite,
    make_goal_surface,
    make_player_sprite,
    make_powerup_sprite,
)
from cipher.render.ui import draw_bar, draw_match_hud_header
from cipher.scenes.base import Scene


class MatchScene(Scene):
    def enter(self, **kwargs: Any) -> None:
        self.arena_id = kwargs.get("arena_id", "neon_sphere")
        self.difficulty = kwargs.get("difficulty", "Operative")
        self.mode = kwargs.get("mode", "quick")  # quick | challenge
        self.challenge_index = kwargs.get("challenge_index", 0)

        profile = DIFFICULTY_PROFILES.get(self.difficulty, DIFFICULTY_PROFILES["Operative"])
        self.ball_speed_mul = float(profile["ball_speed_mul"])
        self.powerup_mul = float(profile["powerup_interval_mul"])

        self.arena = create_arena(self.arena_id)
        self.state = MatchState()
        duration = float(ARENA_MATCH_SECONDS.get(self.arena_id, DEFAULT_MATCH_SECONDS))
        self.state.configure_duration(duration)
        self.camera = CameraFX()
        self.particles = ParticleSystem()
        self.starfield = Starfield(seed=hash(self.arena_id) % 9999)
        self.t = 0.0

        ax, ay = self.arena.player_spawn
        ex, ey = self.arena.enemy_spawn
        self.player = Player(ax, ay, team="vex", name="VEX", facing_x=1.0)
        self.enemy = Player(
            ex, ey, team="foe", name=AI_NAMES.get(self.difficulty, "NULL"), facing_x=-1.0
        )
        bx, by = self.arena.ball_spawn
        self.balls: list[Ball] = [Ball(bx, by)]
        self.primary_ball = self.balls[0]

        self.powers = PowerUpManager(interval_mul=self.powerup_mul)
        self.powers.set_spawn_points(self.arena.powerup_spawns)
        self.ai = AIController(self.difficulty)

        self._goal_frame = 0
        self._paused = False
        self._result_sent = False

        # hit edge tracking
        self._player_was_charging = False
        self._enemy_was_charging = False

        MUSIC.play("match")
        SFX.play("countdown")

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state.phase != MatchPhase.OVER:
                self._paused = not self._paused
                if self._paused:
                    from cipher.scenes.pause import PauseScene

                    self.app.push_scene(PauseScene(self.app), match=self)
            return

    def fixed_update(self, dt: float) -> None:
        if self._paused:
            return
        self.t += dt
        self._goal_frame = int(self.t * 10)
        self.starfield.update(dt)
        self.camera.update(dt)
        self.particles.update(dt)

        events = self.state.update_phase(dt)
        for ev in events:
            if ev == "countdown_tick":
                SFX.play("countdown")
            elif ev == "go":
                SFX.play("go")
            elif ev == "reset_round":
                self._reset_positions()
            elif ev == "time_up":
                SFX.play("countdown")
            elif ev == "match_over":
                self._finish_match()

        if self.state.phase == MatchPhase.OVER:
            return

        if self.state.phase != MatchPhase.PLAYING:
            # still animate lightly
            self.arena.update_hazards(dt)
            return

        self._update_playing(dt)

    def _finish_match(self) -> None:
        if self._result_sent:
            return
        self._result_sent = True
        won = self.state.winner == "player"
        # Draw at buzzer still uses lose stinger if not a win
        SFX.play("win" if won else "lose")
        points = compute_points(
            self.state.player_score,
            self.state.enemy_score,
            self.difficulty,
            won,
            self.state.match_time,
        )
        from cipher.scenes.results import ResultsScene

        self.app.replace_scene(
            ResultsScene(self.app),
            won=won,
            player_score=self.state.player_score,
            enemy_score=self.state.enemy_score,
            points=points,
            mode=self.mode,
            arena_id=self.arena_id,
            difficulty=self.difficulty,
            challenge_index=self.challenge_index,
            match_time=self.state.match_time,
        )

    def _reset_positions(self) -> None:
        """Reset entities and wipe all leftover FX from the previous point."""
        ax, ay = self.arena.player_spawn
        ex, ey = self.arena.enemy_spawn
        bx, by = self.arena.ball_spawn
        self.player.x, self.player.y = ax, ay
        self.player.vx = self.player.vy = 0.0
        self.player.charge = 0.0
        self.player.dash_timer = 0.0
        self.player.invuln = 0.0
        self.enemy.x, self.enemy.y = ex, ey
        self.enemy.vx = self.enemy.vy = 0.0
        self.enemy.charge = 0.0
        self.enemy.dash_timer = 0.0
        self.enemy.invuln = 0.0
        # keep one primary ball
        self.balls = [Ball(bx, by)]
        self.primary_ball = self.balls[0]
        # Clear ALL residual effects (particles, trails, camera juice)
        self._clear_all_fx()

    def _clear_all_fx(self) -> None:
        self.particles.clear()
        # Rebuild empty trails on players / balls
        from cipher.render.fx import Trail

        self.player.trail = Trail(10)
        self.enemy.trail = Trail(10)
        for b in self.balls:
            b.trail = Trail(14)
        # Stop screen shake / flash carry-over
        self.camera.shake_time = 0.0
        self.camera.shake_mag = 0.0
        self.camera.offset_x = 0.0
        self.camera.offset_y = 0.0
        self.camera.flash_time = 0.0
        self.camera.chromatic = 0.0
        self.app.camera_offset = (0.0, 0.0)

    def _update_playing(self, dt: float) -> None:
        inp = self.app.input
        # Player input
        prev_dash_cd = self.player.dash_cd
        self.player.apply_input(inp.move_x, inp.move_y, inp.dash_pressed, inp.hit_held, dt)
        if self.player.dash_cd > prev_dash_cd - 0.01 and inp.dash_pressed and self.player.dash_timer > 0:
            SFX.play("dash")
            self.particles.emit(self.player.x, self.player.y, 12, CYAN, speed=200, life=0.3)

        # charge start tick
        if self.player.charging and not self._player_was_charging:
            SFX.play("charge", 0.6)

        # AI
        ball = self._closest_ball(self.enemy.x, self.enemy.y)
        mx, my, dash, hit = self.ai.update(
            dt,
            self.enemy,
            ball,
            self.arena.right_goal.center[0],
            self.arena.right_goal.center[1],
            self.arena.left_goal.center[0],
            self.arena.left_goal.center[1],
            (
                self.arena.bounds.left,
                self.arena.bounds.top,
                self.arena.bounds.right,
                self.arena.bounds.bottom,
            ),
        )
        prev_e = self.enemy.dash_cd
        self.enemy.apply_input(mx, my, dash, hit, dt)
        if dash and self.enemy.dash_timer > 0 and self.enemy.dash_cd >= prev_e:
            SFX.play("dash", 0.5)
            self.particles.emit(self.enemy.x, self.enemy.y, 10, MAGENTA, speed=180, life=0.25)

        # Player shot: release Space fires charged (or tap) shot
        if inp.hit_released or (self._player_was_charging and not self.player.charging):
            if self.player.charge > 0.0:
                self._try_hit(self.player, release=True)
        elif inp.hit_held and self.player.charge < 0.12:
            # early hold = soft continuous dribble nudge
            self._try_hit(self.player, release=False)

        self._player_was_charging = self.player.charging

        # AI dump charge when ready near ball
        if self.enemy.charge > 0.4 and dist(
            self.enemy.x, self.enemy.y, ball.x, ball.y
        ) < self.enemy.influence:
            self._try_hit(self.enemy, release=True)
        elif hit and self.enemy.charge > 0.55:
            self._try_hit(self.enemy, release=True)

        self.player.update_timers(dt)
        self.enemy.update_timers(dt)
        self.player.integrate(dt)
        self.enemy.integrate(dt)

        # soft magnet on ball — only when NOT overlapping (prevents sink-through)
        for pl in (self.player, self.enemy):
            for b in self.balls:
                if not b.active:
                    continue
                d = dist(pl.x, pl.y, b.x, b.y)
                touch = pl.radius + b.radius + 2.0
                if touch < d < pl.influence:
                    nx, ny = normalize(pl.x - b.x, pl.y - b.y)
                    pull = PLAYER_MAGNET_STRENGTH * (1.0 - d / pl.influence) * dt
                    if pl.overdrive:
                        pull *= 1.4
                    b.vx += nx * pull * 0.35
                    b.vy += ny * pull * 0.35

        # arena gravity
        sign = -1.0 if self.powers.gravity_flip else 1.0
        ents = [self.player, self.enemy] + [b for b in self.balls if b.active]
        self.arena.apply_forces(ents, dt, gravity_sign=sign)
        self.arena.update_hazards(dt)

        max_ball = BALL_MAX_SPEED * self.ball_speed_mul
        # Substep ball motion to stop tunneling through players at high speed
        ball_steps = 4
        sub_dt = dt / ball_steps
        ball_hit_sfx = False
        for _ in range(ball_steps):
            for b in self.balls:
                if not b.active:
                    continue
                b.x, b.y = b.x + b.vx * sub_dt, b.y + b.vy * sub_dt
                # player-ball each substep — solid separation + kick
                for pl in (self.player, self.enemy):
                    rest = BALL_RESTITUTION
                    if pl.dash_timer > 0:
                        rest = max(rest, 0.95)
                    (
                        pl.x,
                        pl.y,
                        pl.vx,
                        pl.vy,
                        b.x,
                        b.y,
                        b.vx,
                        b.vy,
                        hitb,
                    ) = resolve_circle_circle(
                        pl.x,
                        pl.y,
                        pl.vx,
                        pl.vy,
                        pl.radius,
                        PLAYER_MASS,
                        b.x,
                        b.y,
                        b.vx,
                        b.vy,
                        b.radius,
                        BALL_MASS,
                        restitution=rest,
                        sep_slop=1.25,
                    )
                    if hitb:
                        boost = PLAYER_HIT_FORCE * 0.28
                        if pl.overdrive:
                            boost *= 1.5
                        if pl.dash_timer > 0:
                            boost *= 1.35
                        b.vx += pl.facing_x * boost * 0.14 + pl.vx * 0.18
                        b.vy += pl.facing_y * boost * 0.14 + pl.vy * 0.18
                        b.vx, b.vy = clamp_speed(b.vx, b.vy, max_ball)
                        if not ball_hit_sfx:
                            SFX.play("bounce", 0.4)
                            ball_hit_sfx = True
                        self.particles.emit(b.x, b.y, 4, pl.color, speed=100, life=0.18)

        for b in self.balls:
            if not b.active:
                continue
            b.vx, b.vy = apply_friction(b.vx, b.vy, BALL_FRICTION, dt)
            b.vx, b.vy = clamp_speed(b.vx, b.vy, max_ball)
            b.trail.add(b.x, b.y)
            b.trail.update(dt)
            b.frame += 1

        # wall collisions — players (never leave embedded / stuck)
        bds = self.arena.bounds
        gy = (self.arena.left_goal.center[1], GOAL_HEIGHT / 2)
        for pl in (self.player, self.enemy):
            pl.x, pl.y, pl.vx, pl.vy, hitw, _ = resolve_circle_rect_bounds(
                pl.x,
                pl.y,
                pl.vx,
                pl.vy,
                pl.radius,
                bds.left,
                bds.top,
                bds.right,
                bds.bottom,
                restitution=0.25,
            )
            if self.arena.collide_hazards(pl, is_ball=False):
                self.camera.shake(3, 0.08)
            # re-clamp after hazards so they never stick in walls
            pl.x, pl.y = clamp_entity_in_bounds(
                pl.x, pl.y, pl.radius, bds.left, bds.top, bds.right, bds.bottom
            )
            pl.vx, pl.vy = kill_inward_velocity_at_bounds(
                pl.x, pl.y, pl.vx, pl.vy, pl.radius,
                bds.left, bds.top, bds.right, bds.bottom,
            )

        for b in self.balls:
            if not b.active:
                continue
            b.x, b.y, b.vx, b.vy, hitw, side = resolve_circle_rect_bounds(
                b.x,
                b.y,
                b.vx,
                b.vy,
                b.radius,
                bds.left,
                bds.top,
                bds.right,
                bds.bottom,
                restitution=BALL_WALL_RESTITUTION,
                skip_left_goal=gy,
                skip_right_goal=gy,
            )
            if hitw:
                SFX.play("wall", 0.5)
                self.particles.trail(b.x, b.y, CYAN, b.vx, b.vy)
            if self.arena.collide_hazards(b, is_ball=True):
                SFX.play("bounce", 0.6)
                self.camera.shake(2, 0.06)

        # player-player solid body + dash bounce (two passes for full separation)
        dash_hit = self.player.dash_timer > 0 or self.enemy.dash_timer > 0
        rest_pp = 0.9 if dash_hit else 0.6
        phit = False
        for _pass in range(2):
            (
                self.player.x,
                self.player.y,
                self.player.vx,
                self.player.vy,
                self.enemy.x,
                self.enemy.y,
                self.enemy.vx,
                self.enemy.vy,
                hit_now,
            ) = resolve_circle_circle(
                self.player.x,
                self.player.y,
                self.player.vx,
                self.player.vy,
                self.player.radius,
                PLAYER_MASS,
                self.enemy.x,
                self.enemy.y,
                self.enemy.vx,
                self.enemy.vy,
                self.enemy.radius,
                PLAYER_MASS,
                restitution=rest_pp,
                sep_slop=1.5,
            )
            phit = phit or hit_now
        if phit:
            SFX.play("hit", 0.45)
            if dash_hit:
                # Extra knockback when a dash connects
                dx = self.enemy.x - self.player.x
                dy = self.enemy.y - self.player.y
                nx, ny = normalize(dx, dy)
                kick = 240.0
                if self.player.dash_timer > 0:
                    self.enemy.vx += nx * kick
                    self.enemy.vy += ny * kick
                if self.enemy.dash_timer > 0:
                    self.player.vx -= nx * kick
                    self.player.vy -= ny * kick
                self.camera.shake(5, 0.1)
            # Keep both in bounds after body check (no stick against walls)
            for pl in (self.player, self.enemy):
                pl.x, pl.y = clamp_entity_in_bounds(
                    pl.x, pl.y, pl.radius, bds.left, bds.top, bds.right, bds.bottom
                )
                pl.vx, pl.vy = kill_inward_velocity_at_bounds(
                    pl.x, pl.y, pl.vx, pl.vy, pl.radius,
                    bds.left, bds.top, bds.right, bds.bottom,
                )

        # Final player-ball pass (catch residual overlaps after walls / body checks)
        for pl in (self.player, self.enemy):
            for b in self.balls:
                if not b.active:
                    continue
                (
                    pl.x,
                    pl.y,
                    pl.vx,
                    pl.vy,
                    b.x,
                    b.y,
                    b.vx,
                    b.vy,
                    hitb,
                ) = resolve_circle_circle(
                    pl.x,
                    pl.y,
                    pl.vx,
                    pl.vy,
                    pl.radius,
                    PLAYER_MASS,
                    b.x,
                    b.y,
                    b.vx,
                    b.vy,
                    b.radius,
                    BALL_MASS,
                    restitution=BALL_RESTITUTION,
                    sep_slop=1.25,
                )
                if hitb:
                    b.vx += pl.facing_x * PLAYER_HIT_FORCE * 0.1
                    b.vy += pl.facing_y * PLAYER_HIT_FORCE * 0.1
                    b.vx, b.vy = clamp_speed(b.vx, b.vy, max_ball)

        # ball-ball
        active_balls = [b for b in self.balls if b.active]
        for i in range(len(active_balls)):
            for j in range(i + 1, len(active_balls)):
                a, b = active_balls[i], active_balls[j]
                (
                    a.x,
                    a.y,
                    a.vx,
                    a.vy,
                    b.x,
                    b.y,
                    b.vx,
                    b.vy,
                    _,
                ) = resolve_circle_circle(
                    a.x, a.y, a.vx, a.vy, a.radius, BALL_MASS,
                    b.x, b.y, b.vx, b.vy, b.radius, BALL_MASS,
                    restitution=0.95,
                )

        # powerups
        pev = self.powers.update(dt)
        if pev == "spawn":
            SFX.play("powerup_spawn", 0.7)
        for pl in (self.player, self.enemy):
            got = self.powers.try_pickup(pl.x, pl.y, pl.radius)
            if got:
                SFX.play("powerup")
                self.powers.apply(got.kind, pl, self.balls, self.arena.bounds.center)
                self.particles.burst(pl.x, pl.y, pl.color, 1.2)
                self.camera.flash(pl.color, 80, 0.1)

        # trails particles
        if self.player.dash_timer > 0:
            self.particles.trail(self.player.x, self.player.y, CYAN, self.player.vx, self.player.vy)
        if self.enemy.dash_timer > 0:
            self.particles.trail(self.enemy.x, self.enemy.y, MAGENTA, self.enemy.vx, self.enemy.vy)
        for b in self.balls:
            if b.active and b.speed > 200:
                self.particles.trail(b.x, b.y, WHITE_GLOW, b.vx, b.vy)

        # goals
        for b in list(self.balls):
            if not b.active:
                continue
            scorer = self.arena.goal_check(b.x, b.y, b.radius)
            if scorer:
                # shield blocks own goal
                if scorer == "enemy" and self.player.consume_shield():
                    b.vx = abs(b.vx) + 200
                    b.x = self.arena.bounds.left + 80
                    self.particles.burst(b.x, b.y, CYAN, 1.5)
                    SFX.play("powerup")
                    continue
                if scorer == "player" and self.enemy.consume_shield():
                    b.vx = -abs(b.vx) - 200
                    b.x = self.arena.bounds.right - 80
                    self.particles.burst(b.x, b.y, MAGENTA, 1.5)
                    SFX.play("powerup")
                    continue
                self._on_goal(scorer, b)
                break

        self.balls = [b for b in self.balls if b.active]
        if not self.balls:
            bx, by = self.arena.ball_spawn
            self.balls = [Ball(bx, by)]
            self.primary_ball = self.balls[0]

    def _on_goal(self, scorer: str, ball: Ball) -> None:
        self.state.score(scorer)
        SFX.play("goal")
        self.camera.goal_burst()
        color = CYAN if scorer == "player" else MAGENTA
        self.particles.burst(ball.x, ball.y, color, 2.0)
        self.particles.emit(ball.x, ball.y, 30, WHITE_GLOW, speed=280, life=0.6)
        if ball.is_extra:
            ball.active = False
        else:
            # freeze will reset
            ball.vx = ball.vy = 0

    def _try_hit(self, pl: Player, release: bool) -> None:
        best = None
        best_d = 1e9
        for b in self.balls:
            if not b.active:
                continue
            d = dist(pl.x, pl.y, b.x, b.y)
            if d < pl.influence and d < best_d:
                best_d = d
                best = b
        if best is None:
            if release:
                pl.charge = 0.0
            return
        if release:
            force = pl.release_shot_force()
            if pl.overdrive:
                force *= 1.35
            fx, fy = pl.facing_x, pl.facing_y
            # aim assist toward enemy goal
            if pl.team == "vex":
                gx, gy = self.arena.right_goal.center
            else:
                gx, gy = self.arena.left_goal.center
            ax, ay = normalize(gx - pl.x, gy - pl.y)
            fx = fx * 0.65 + ax * 0.35
            fy = fy * 0.65 + ay * 0.35
            fx, fy = normalize(fx, fy)
            best.vx += fx * force + pl.vx * 0.35
            best.vy += fy * force + pl.vy * 0.35
            max_ball = BALL_MAX_SPEED * self.ball_speed_mul
            best.vx, best.vy = clamp_speed(best.vx, best.vy, max_ball)
            SFX.play("launch")
            self.particles.burst(best.x, best.y, pl.color, 1.0)
            self.camera.impact(5)
        else:
            # light continuous poke
            if pl.charge > 0.15:
                return  # charging for big shot
            fx, fy = pl.facing_x, pl.facing_y
            best.vx += fx * PLAYER_HIT_FORCE * 0.02
            best.vy += fy * PLAYER_HIT_FORCE * 0.02

    def _closest_ball(self, x: float, y: float) -> Ball:
        active = [b for b in self.balls if b.active]
        if not active:
            return self.primary_ball
        return min(active, key=lambda b: dist(x, y, b.x, b.y))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self.starfield.draw(surface)
        self.arena.draw_floor(surface, self.t)

        # goals (animated energy mesh)
        lg = self.arena.left_goal.rect
        rg = self.arena.right_goal.rect
        gl = make_goal_surface(GOAL_HEIGHT, "left", self._goal_frame)
        gr = make_goal_surface(GOAL_HEIGHT, "right", self._goal_frame)
        surface.blit(gl, gl.get_rect(centery=lg.centery, left=lg.left - 10))
        surface.blit(gr, gr.get_rect(centery=rg.centery, right=rg.right + 10))

        self.arena.draw_hazards(surface, self.t)

        # powerups
        for p in self.powers.items:
            spr = make_powerup_sprite(p.kind, p.frame // 2)
            surface.blit(spr, spr.get_rect(center=(int(p.x), int(p.y))))

        # trails & particles under entities
        self.player.trail.draw(surface, CYAN, 5)
        self.enemy.trail.draw(surface, MAGENTA, 5)
        for b in self.balls:
            if b.active:
                b.trail.draw(surface, WHITE_GLOW, 4)

        self.particles.draw(surface)

        # players — classic arcade sports humanoids (flip by facing, not full spin)
        for pl in (self.player, self.enemy):
            speed = vec_length(pl.vx, pl.vy)
            if pl.dash_timer > 0:
                anim = "dash"
                fr = pl.frame // 2
            elif speed > 50:
                anim = "move"
                fr = pl.frame // 3
            else:
                anim = "idle"
                fr = pl.frame // 5
            spr = make_player_sprite(pl.team, fr, anim)
            # Face left/right for sports readability (Blitz-style presentation)
            if pl.facing_x < -0.15:
                spr = pygame.transform.flip(spr, True, False)
            # slight lean into vertical movement
            if abs(pl.facing_y) > 0.55 and speed > 40:
                lean = -6 if pl.facing_y < 0 else 6
                spr = pygame.transform.rotate(spr, lean)
            # Stadium foot light + contact shadow (arcade sports polish)
            glow_col = CYAN if pl.team == "vex" else MAGENTA
            pygame.draw.ellipse(
                surface,
                with_alpha(glow_col, 60),
                (int(pl.x) - 26, int(pl.y) + 18, 52, 18),
            )
            pygame.draw.ellipse(
                surface,
                with_alpha((0, 0, 0), 90),
                (int(pl.x) - 18, int(pl.y) + 26, 36, 12),
            )
            # Draw larger athletes slightly above collision center
            surface.blit(spr, spr.get_rect(center=(int(pl.x), int(pl.y) - 10)))
            px, py = int(pl.x), int(pl.y)
            if pl.shield:
                col = CYAN if pl.team == "vex" else MAGENTA
                for rad, alpha in ((pl.radius + 16, 40), (pl.radius + 12, 100), (pl.radius + 9, 170)):
                    pygame.draw.circle(surface, with_alpha(col, alpha), (px, py - 8), rad, 2)
            if pl.overdrive:
                for i in range(3):
                    rad = pl.radius + 12 + i * 5 + int(2 * math.sin(self.t * 10 + i))
                    pygame.draw.circle(surface, with_alpha(YELLOW, 95 - i * 25), (px, py - 8), rad, 1)

        # balls
        for b in self.balls:
            if not b.active:
                continue
            spr = make_ball_sprite(b.frame // 2)
            surface.blit(spr, spr.get_rect(center=(int(b.x), int(b.y))))

        self.camera.draw_flash(surface)
        self._draw_hud(surface)

        # countdown / goal overlays
        if self.state.phase == MatchPhase.COUNTDOWN:
            val = max(1, int(math.ceil(self.state.phase_timer)))
            if self.state.phase_timer <= 0.15:
                txt = "GO!"
            else:
                txt = str(val)
            draw_text(surface, txt, (INTERNAL_W // 2, INTERNAL_H // 2), 96, CYAN, center=True)
        elif self.state.phase == MatchPhase.GOAL:
            who = "VEX SCORES!" if self.state.last_scorer == "player" else f"{self.enemy.name} SCORES!"
            col = CYAN if self.state.last_scorer == "player" else MAGENTA
            draw_text(surface, who, (INTERNAL_W // 2, INTERNAL_H // 2), 48, col, center=True)

        # apply shake by offsetting — done in app via camera; store offsets on app
        self.app.camera_offset = (self.camera.offset_x, self.camera.offset_y)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        draw_match_hud_header(
            surface,
            self.state.player_score,
            self.state.enemy_score,
            "VEX",
            self.enemy.name[:6].upper(),
            self.state.time_remaining,
            ARENA_NAMES.get(self.arena_id, self.arena_id).upper(),
            self.difficulty.upper(),
        )

        # Ability meters (sports TV lower-third style)
        draw_text(surface, "CHARGE", (28, INTERNAL_H - 54), 14, CYAN)
        draw_bar(surface, pygame.Rect(28, INTERNAL_H - 34, 170, 14), self.player.charge, CYAN)
        dash_ready = 1.0 - min(1.0, self.player.dash_cd / 0.85) if self.player.dash_cd > 0 else 1.0
        draw_text(surface, "DASH", (214, INTERNAL_H - 54), 14, YELLOW)
        draw_bar(surface, pygame.Rect(214, INTERNAL_H - 34, 110, 14), dash_ready, YELLOW)

        sx = 350
        if self.player.speed_time > 0:
            draw_text(surface, "SPD", (sx, INTERNAL_H - 36), 16, YELLOW)
            sx += 48
        if self.player.shield:
            draw_text(surface, "SHD", (sx, INTERNAL_H - 36), 16, CYAN)
            sx += 48
        if self.player.overdrive:
            draw_text(surface, "OVR", (sx, INTERNAL_H - 36), 16, MAGENTA)
            sx += 48
        if self.powers.gravity_flip:
            draw_text(surface, "GRAV", (sx, INTERNAL_H - 36), 16, PURPLE)

        draw_text(surface, "ESC  PAUSE", (INTERNAL_W - 110, INTERNAL_H - 28), 14, WHITE_GLOW, alpha=150)
