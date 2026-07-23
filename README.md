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

Download and run the setup package from this repository:

- **[v1.0/Cipher_v1.0_Setup.exe](./v1.0/Cipher_v1.0_Setup.exe)** — one-click install, Desktop + Start Menu shortcuts, no Python required

Or grab the same build from the [**Releases**](https://github.com/kxz0tn/Cipher/releases) page when available.

### Run from source

See [v1.0/README.md](./v1.0/README.md) for Python setup, controls, and packaging notes.

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
├── v1.0/                 # Versioned release (self-contained)
│   ├── main.py
│   ├── cipher/           # Game package (source + original assets)
│   ├── logo.png          # Branding
│   ├── cipher.ico        # Windows icon
│   ├── installer/        # Inno Setup script
│   ├── Cipher_v1.0_Setup.exe
│   └── README.md
├── README.md             # This overview
└── .gitignore
```

Version folders stay self-contained so future releases can land as **`v1.1/`**, **`v1.2/`**, and so on without disturbing older lines.

---

## Features (v1.0)

- **Arena sport gameplay** — score into goals, defend your net, charge shots and dash  
- **Three arenas** — Neon Sphere, Debris Field, Gravity Well  
- **Quick Match & Challenge Mode** — pick arena/difficulty or climb the ladder  
- **Power-ups** — speed, shield, overdrive, multi-ball, gravity flip  
- **Procedural audio** — synth music and SFX (no third-party sample packs)  
- **High scores** — unique names, wins only; stored under `%LocalAppData%\Cipher\`  

---

## Links

- **Source (v1.0):** [v1.0/](./v1.0/)  
- **Installer:** [v1.0/Cipher_v1.0_Setup.exe](./v1.0/Cipher_v1.0_Setup.exe)  
- **Releases:** [github.com/kxz0tn/Cipher/releases](https://github.com/kxz0tn/Cipher/releases)  
- **Issues:** [github.com/kxz0tn/Cipher/issues](https://github.com/kxz0tn/Cipher/issues)  

---

## Credits

Built with **Python** and **pygame-ce**.  
All game code, logo, icon, art, and installer packaging in this repository are original project content.

**Cipher v1.0** — *Score · Defend · Dominate*.
