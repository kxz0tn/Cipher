"""Prove audio dies for EVERY quit path (Quit menu + simulated window close)."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"


def _run_child(code: str, label: str) -> None:
    tmp = ROOT / "tools" / f"_tmp_{label}.py"
    tmp.write_text(code, encoding="utf-8")
    proc = subprocess.Popen([str(PY), str(tmp)], cwd=str(ROOT))
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise SystemExit(f"FAIL [{label}]: process hung")
    if proc.poll() is None:
        proc.kill()
        raise SystemExit(f"FAIL [{label}]: process still alive")
    time.sleep(0.2)
    if proc.poll() is None:
        raise SystemExit(f"FAIL [{label}]: process still alive after wait")
    print(f"PASS [{label}]: process dead, code={proc.returncode}")
    try:
        tmp.unlink()
    except OSError:
        pass


def test_force_exit() -> None:
    code = f"""
import os, sys, time
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
sys.path.insert(0, r'{ROOT}')
import pygame
pygame.mixer.pre_init(22050,-16,2,512)
pygame.init(); pygame.mixer.init(22050,-16,2,512)
from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.settings import Settings
from cipher.audio.shutdown import force_process_exit
s=Settings(); SFX.bind_settings(s); SFX.build(); MUSIC.bind_settings(s)
MUSIC.play('match'); time.sleep(0.4)
force_process_exit(0)
print('FAIL returned')
"""
    _run_child(code, "force_process_exit")


def test_app_quit_menu_path() -> None:
    """Same path as Main Menu → QUIT."""
    code = f"""
import os, sys, time
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
sys.path.insert(0, r'{ROOT}')
import pygame
pygame.mixer.pre_init(22050,-16,2,512)
pygame.init(); pygame.mixer.init(22050,-16,2,512); pygame.display.set_mode((320,200))
from cipher.app import App
from cipher.settings import Settings
from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
app = App(); app.settings = Settings()
SFX.bind_settings(app.settings); SFX.build(); MUSIC.bind_settings(app.settings)
MUSIC.play('menu'); time.sleep(0.35)
# Menu Quit path
app.quit()
print('FAIL quit returned')
sys.exit(2)
"""
    _run_child(code, "menu_quit_app.quit")


def test_window_close_quit_event() -> None:
    """Same path as window X / Alt+F4 (pygame.QUIT)."""
    code = f"""
import os, sys, time
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
sys.path.insert(0, r'{ROOT}')
import pygame
from cipher.app import App
from cipher.settings import Settings
from cipher.audio.music import MUSIC
from cipher.audio.sfx import SFX
from cipher.scenes.main_menu import MainMenuScene
from cipher.constants import FIXED_DT

app = App(); app.settings = Settings()
pygame.mixer.pre_init(22050,-16,2,512)
pygame.init(); pygame.mixer.init(22050,-16,2,512)
app.virtual = pygame.Surface((1280,720))
app.window = pygame.display.set_mode((640,360))
app.clock = pygame.time.Clock()
SFX.bind_settings(app.settings); SFX.build(); MUSIC.bind_settings(app.settings)
app.running = True
app.push_scene(MainMenuScene(app))
MUSIC.play('menu'); time.sleep(0.3)
# Inject window-close event
pygame.event.post(pygame.event.Event(pygame.QUIT))
app._process_events()  # must call quit -> os._exit
# If we get here, quit failed
print('FAIL QUIT event did not exit')
sys.exit(3)
"""
    _run_child(code, "window_close_QUIT_event")


if __name__ == "__main__":
    test_force_exit()
    test_app_quit_menu_path()
    test_window_close_quit_event()
    print("ALL QUIT PATHS PASSED")
