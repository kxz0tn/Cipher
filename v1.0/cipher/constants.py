"""Global constants and gameplay tuning knobs."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
INTERNAL_W = 1280
INTERNAL_H = 720
TARGET_FPS = 60
FIXED_DT = 1.0 / TARGET_FPS
MAX_FRAME_CATCHUP = 5
WINDOW_TITLE = "Cipher v1.0"
VERSION = "1.0"

# ---------------------------------------------------------------------------
# Palette (cyberpunk neon)
# ---------------------------------------------------------------------------
BG_DEEP = (5, 1, 15)
CYAN = (0, 240, 255)
MAGENTA = (255, 43, 214)
PURPLE = (155, 92, 255)
HOT_PINK = (255, 77, 166)
ELEC_BLUE = (61, 124, 255)
WHITE_GLOW = (232, 247, 255)
GRID = (26, 10, 46)
DANGER = (255, 51, 85)
YELLOW = (255, 220, 60)
ORANGE = (255, 140, 40)
GREEN = (40, 255, 140)
DARK_PANEL = (12, 6, 28)
PANEL_BORDER = (80, 40, 140)

# ---------------------------------------------------------------------------
# Match rules
# ---------------------------------------------------------------------------
GOALS_TO_WIN = 5
COUNTDOWN_SECONDS = 3
GOAL_FREEZE_SECONDS = 1.4
# Countdown match length per arena (seconds) — clean / chaotic / complex
ARENA_MATCH_SECONDS = {
    "neon_sphere": 180,    # 3:00 — pure skill, full clock
    "debris_field": 150,   # 2:30 — hazards, slightly shorter
    "gravity_well": 165,   # 2:45 — gravity play needs room
}
DEFAULT_MATCH_SECONDS = 180

# ---------------------------------------------------------------------------
# Arena layout (playfield inside screen)
# ---------------------------------------------------------------------------
ARENA_MARGIN = 48
GOAL_WIDTH = 28
GOAL_HEIGHT = 160
GOAL_INSET = 4

# ---------------------------------------------------------------------------
# Player (Vex)
# ---------------------------------------------------------------------------
PLAYER_RADIUS = 16
PLAYER_MAX_SPEED = 320.0
PLAYER_ACCEL = 2200.0
PLAYER_FRICTION = 1600.0
PLAYER_DASH_SPEED = 720.0
PLAYER_DASH_TIME = 0.14
PLAYER_DASH_COOLDOWN = 0.85
PLAYER_INFLUENCE_RADIUS = 42.0
PLAYER_HIT_FORCE = 380.0
PLAYER_CHARGE_RATE = 1.15
PLAYER_CHARGE_MAX = 1.0
PLAYER_CHARGE_FORCE_MIN = 420.0
PLAYER_CHARGE_FORCE_MAX = 980.0
PLAYER_MAGNET_STRENGTH = 90.0

# ---------------------------------------------------------------------------
# Ball
# ---------------------------------------------------------------------------
BALL_RADIUS = 11
BALL_MAX_SPEED = 780.0
BALL_FRICTION = 18.0
BALL_RESTITUTION = 0.92
BALL_WALL_RESTITUTION = 0.88
BALL_MASS = 1.0
PLAYER_MASS = 1.6

# ---------------------------------------------------------------------------
# Power-ups
# ---------------------------------------------------------------------------
POWERUP_RADIUS = 14
POWERUP_SPAWN_INTERVAL = 12.0
POWERUP_LIFETIME = 14.0
POWERUP_MAX_ACTIVE = 2
POWERUP_SPEED_DURATION = 6.0
POWERUP_GRAVITY_DURATION = 8.0
POWERUP_SHIELD_DURATION = 10.0
POWERUP_OVERDRIVE_DURATION = 5.0
POWERUP_MULTIBALL_EXTRA_LIFE = 20.0

# ---------------------------------------------------------------------------
# Particles
# ---------------------------------------------------------------------------
PARTICLE_SOFT_CAP = 300

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
SAMPLE_RATE = 22050
AUDIO_CHANNELS = 16

# ---------------------------------------------------------------------------
# Difficulty names
# ---------------------------------------------------------------------------
DIFFICULTIES = ("Initiate", "Operative", "Phantom", "Nightmare")
ARENA_IDS = ("neon_sphere", "debris_field", "gravity_well")
ARENA_NAMES = {
    "neon_sphere": "Neon Sphere",
    "debris_field": "Debris Field",
    "gravity_well": "Gravity Well",
}

# Difficulty multipliers / AI profiles
DIFFICULTY_PROFILES = {
    "Initiate": {
        "ai_reaction": 0.28,
        "ai_aim_error": 0.35,
        "ai_aggression": 0.35,
        "ai_dash_chance": 0.15,
        "ball_speed_mul": 0.88,
        "powerup_interval_mul": 0.7,
        "score_mul": 1.0,
    },
    "Operative": {
        "ai_reaction": 0.16,
        "ai_aim_error": 0.18,
        "ai_aggression": 0.55,
        "ai_dash_chance": 0.35,
        "ball_speed_mul": 1.0,
        "powerup_interval_mul": 1.0,
        "score_mul": 1.5,
    },
    "Phantom": {
        "ai_reaction": 0.08,
        "ai_aim_error": 0.08,
        "ai_aggression": 0.75,
        "ai_dash_chance": 0.55,
        "ball_speed_mul": 1.08,
        "powerup_interval_mul": 1.25,
        "score_mul": 2.5,
    },
    "Nightmare": {
        "ai_reaction": 0.04,
        "ai_aim_error": 0.03,
        "ai_aggression": 0.95,
        "ai_dash_chance": 0.75,
        "ball_speed_mul": 1.18,
        "powerup_interval_mul": 1.6,
        "score_mul": 4.0,
    },
}

# Challenge ladder: (arena_id, difficulty)
CHALLENGE_LADDER = [
    ("neon_sphere", "Initiate"),
    ("neon_sphere", "Operative"),
    ("debris_field", "Operative"),
    ("gravity_well", "Operative"),
    ("debris_field", "Phantom"),
    ("gravity_well", "Phantom"),
    ("neon_sphere", "Nightmare"),
    ("debris_field", "Nightmare"),
    ("gravity_well", "Nightmare"),
]

# AI opponent names by difficulty flavor
AI_NAMES = {
    "Initiate": "Null",
    "Operative": "Riven",
    "Phantom": "Kite",
    "Nightmare": "Spectre",
}
