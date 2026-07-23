# Cipher v1.0

First official release of **Cipher** — a top-down neon arena sports game.

> **Score · Defend · Dominate** · Charged hits · Dashes · Power-ups · Procedural audio

---

## Play options

### Windows installer (recommended)

Double-click:

```
Cipher_v1.0_Setup.exe
```

The installer lets you choose the install location, creates **Desktop** and **Start Menu** shortcuts, and includes a full uninstaller. No Python install required.

### Run from source

**Requirements**

- **Python** 3.11+ (3.13 recommended)
- **pygame-ce** (see `requirements.txt`)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

---

## Layout

```
v1.0/
├── main.py                 # Entry point
├── requirements.txt
├── build.spec              # PyInstaller one-file build
├── cipher.ico              # App / installer icon
├── logo.png                # Title / menu branding
├── Cipher_v1.0_Setup.exe   # Windows installer
├── installer/
│   └── Cipher.iss          # Inno Setup script
├── cipher/                 # Game package
│   ├── app.py
│   ├── assets/             # Original sprites, UI, logo
│   ├── audio/              # Procedural music & SFX
│   ├── gameplay/
│   ├── render/
│   └── scenes/
├── tests/
└── README.md
```

High scores and settings are **not** written next to the game. They live under:

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
- Hard audio teardown on quit (no stuck sound)  
- Original cyberpunk logo and multi-size Windows icon  

---

## Packaging notes

To rebuild the one-file game binary:

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm build.spec
```

To rebuild the Windows installer (requires [Inno Setup 6](https://jrsoftware.org/isinfo.php)):

```bash
ISCC installer\Cipher.iss
```

Output: `dist\Cipher_v1.0_Setup.exe` (see project packaging docs).

---

## Original content

This release contains **only original project content**:

- All Python source  
- Game art, logo, and icon created for Cipher  
- Procedural audio implementation  
- Installer script and packaged installer  

Third-party libraries (Python, pygame-ce, PyInstaller runtime, etc.) remain under their own licenses and are dependencies or binary embeds — not claimed as original game assets.

---

## Version

**Cipher v1.0** — first official public release.  
Future lines will ship as sibling folders (`v1.1/`, `v1.2/`, …) in the same style.
