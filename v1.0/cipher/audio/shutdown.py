"""Hard audio teardown for every exit path (Quit menu, window X, Alt+F4).

Windows + SDL can leave audio playing if the process dies while the mixer
still owns an open device. Alt+F4 often works because the OS destroys the
window first; menu Quit must explicitly release the device the same way.
"""
from __future__ import annotations

import os
import time

_shut_down = False


def _safe(fn) -> None:
    try:
        fn()
    except Exception:
        pass


def shutdown_audio(*, force: bool = False) -> None:
    """Mute, stop, and fully uninitialize the mixer. Safe to call repeatedly."""
    global _shut_down
    if _shut_down and not force:
        return

    # --- application players ---
    try:
        from cipher.audio.music import MUSIC

        _safe(MUSIC.hard_stop)
    except Exception:
        pass

    try:
        from cipher.audio.sfx import SFX

        _safe(SFX.stop_all)
    except Exception:
        pass

    # --- raw pygame / SDL mixer ---
    try:
        import pygame

        # Do NOT gate on pygame.get_init() — mixer can outlive display state.
        if pygame.mixer.get_init() is not None:
            # Mute everything first (prevents residual buffer play-out)
            _safe(lambda: pygame.mixer.set_num_channels(32))
            for i in range(32):
                def _mute_ch(i=i):
                    ch = pygame.mixer.Channel(i)
                    ch.set_volume(0.0)
                    ch.stop()

                _safe(_mute_ch)
            _safe(pygame.mixer.stop)
            _safe(pygame.mixer.music.stop)
            _safe(pygame.mixer.music.unload)
            _safe(lambda: pygame.mixer.set_num_channels(0))
            # Give the audio thread a moment to drop buffers, then quit device
            time.sleep(0.03)
            _safe(pygame.mixer.quit)

        # Second pass if mixer somehow re-inited
        if pygame.mixer.get_init() is not None:
            _safe(pygame.mixer.stop)
            _safe(pygame.mixer.quit)
    except Exception:
        pass

    _shut_down = True


def force_process_exit(code: int = 0) -> None:
    """Full exit used by Quit menu, window close, and Alt+F4.

    Order is intentional for Windows audio drivers:
      1) stop/mute all sounds
      2) quit mixer (release device)
      3) quit display (destroy HWND — same as OS close path)
      4) pygame.quit()
      5) os._exit so no thread can keep the process alive
    """
    shutdown_audio(force=True)

    try:
        import pygame

        # Destroy window before killing process (critical for device release)
        if pygame.display.get_init():
            _safe(pygame.display.quit)
        _safe(pygame.quit)
    except Exception:
        pass

    # Brief pause so OS audio endpoint can drop the stream
    try:
        time.sleep(0.05)
    except Exception:
        pass

    # Final belt: try mixer one more time in case pygame.quit re-touched it
    try:
        import pygame

        if pygame.mixer.get_init() is not None:
            _safe(pygame.mixer.stop)
            _safe(pygame.mixer.quit)
    except Exception:
        pass

    os._exit(int(code) if code is not None else 0)
