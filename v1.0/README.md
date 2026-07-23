# Cipher v1.0

First official source release of **Cipher** — a top-down neon arena sports game.

> **Score · Defend · Dominate** · Charged hits · Dashes · Power-ups · Procedural audio

---

## Requirements

- **Python** 3.11+ (3.13 recommended)
- **pygame-ce** (see `requirements.txt`)

```bash
pip install -r requirements.txt
```

---

## Run from source

From this folder (`v1.0/`):

```bash
python main.py
```

**Expected layout:**

```
v1.0/
├── main.py              # Game entry point
├── requirements.txt
├── logo.png             # Title / menu branding
├── cipher.ico           # Windows icon
├── cipher/              # Game package
│   ├── assets/          # Original sprites & UI art
│   ├── audio/           # Procedural music & SFX
│   ├── gameplay/
│   ├── render/
│   └── scenes/
└── README.md
```

High scores and settings are **not** written next to the game. They are saved under:

```
%LocalAppData%\Cipher\
```

This keeps saves writable after packaging and across updates.

---

## Controls

| Action | Keys |
|--------|------|
| Move | `WASD` / Arrow keys |
| Dash | `Left Shift` |
| Charge / Hit | `Space` |
| Pause | `Esc` |
| Fullscreen | `F11` |
| Confirm / Back | `Enter` / `Esc` |

---

## Modes

| Mode | Description |
|------|-------------|
| **Quick Match** | Pick arena + difficulty |
| **Challenge Mode** | Ladder across arenas and difficulties |

### Arenas

1. **Neon Sphere** — clean glowing pitch  
2. **Debris Field** — asteroids and energy barriers  
3. **Gravity Well** — central pull and energy rings  

### High scores

- Saved only on a **win** (not loss or draw)  
- Names must be **unique** on the board  
- Stored in `%LocalAppData%\Cipher\highscores.json`  

---

## Features

- Solid player / ball / wall physics with dash bounce  
- Match countdown timer per arena  
- Hard audio teardown on quit  
- Original cyberpunk logo and multi-size Windows icon  

---

## Packaging notes

Windows installer / one-file builds are published on the repository  
[**Releases**](https://github.com/kxz0tn/Cipher/releases) page only:

- **[Cipher_v1.0_Setup.exe](https://github.com/kxz0tn/Cipher/releases/download/v1.0/Cipher_v1.0_Setup.exe)**

Packaged binaries are **not** stored in this source tree.

---

## Original content

This release contains **only original project content**:

- All Python source  
- Game art, logo, and icon created for Cipher  
- Procedural audio implementation  

Third-party libraries (Python, pygame-ce, etc.) remain under their own licenses.

---

## Version

**Cipher v1.0** — first official public release.  
Version name stays **v1.0** for this public source line until a future major update.
