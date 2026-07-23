# Cipher

**Neon arena sport** — top-down cyberpunk goals, charged hits, dashes, power-ups, and procedural audio.

| | |
|---|---|
| **Current version** | [v1.0](./v1.0/) |
| **Platform** | Windows (Python source + installer) |
| **License** | MIT — original source & assets only |
| **Status** | Active — first public release |

---

## Play Cipher

### Windows installer (recommended)

Download the latest setup from the [**Releases**](https://github.com/kxz0tn/Cipher/releases) page:

- **[Cipher_v1.0_Setup.exe](https://github.com/kxz0tn/Cipher/releases/download/v1.0/Cipher_v1.0_Setup.exe)** — one-click install, desktop shortcut, no Python required

### Run from source

See [v1.0/README.md](./v1.0/README.md) for Python setup and controls.

```bash
cd v1.0
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Repository layout

```
Cipher/
├── v1.0/                 # Versioned source release
│   ├── main.py
│   ├── cipher/           # Game package + original assets
│   ├── logo.png / cipher.ico
│   ├── requirements.txt
│   └── README.md
├── README.md             # This overview
├── LICENSE
└── .gitignore
```

Versioned folders keep each public release self-contained and easy to archive.  
Future lines ship as **`v1.1/`**, **`v1.2/`**, and so on.

Installers and packaged `.exe` builds are **not** stored in the repository — only on [Releases](https://github.com/kxz0tn/Cipher/releases).

---

## Features (v1.0)

- **Arena sport gameplay** — score into goals, defend your net, charge shots and dash  
- **Three arenas** — Neon Sphere, Debris Field, Gravity Well  
- **Quick Match & Challenge Mode** — pick arena/difficulty or climb the ladder  
- **Power-ups** — speed, shield, overdrive, multi-ball, gravity flip  
- **Procedural audio** — synth music and SFX  
- **High scores** — unique names, wins only; stored under `%LocalAppData%\Cipher\`  

---

## Links

- **Source (v1.0):** [v1.0/](./v1.0/)  
- **Releases / installer:** [github.com/kxz0tn/Cipher/releases](https://github.com/kxz0tn/Cipher/releases)  
- **Issues:** [github.com/kxz0tn/Cipher/issues](https://github.com/kxz0tn/Cipher/issues)  

---

## Credits

Built with **Python** and **pygame-ce**.  
All game code, logo, icon, and art in this repository are original project content.

**Cipher v1.0** — *Score · Defend · Dominate*.
