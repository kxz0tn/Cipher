#!/usr/bin/env python3
"""Cipher v1.0 — entry point."""
from __future__ import annotations

import atexit
import sys


def main() -> int:
    from cipher.audio.shutdown import force_process_exit, shutdown_audio

    atexit.register(lambda: shutdown_audio(force=True))

    from cipher.app import App

    try:
        app = App()
        return app.run()
    except SystemExit as e:
        shutdown_audio(force=True)
        code = e.code if isinstance(e.code, int) else 0
        force_process_exit(code if code is not None else 0)
    except BaseException:
        shutdown_audio(force=True)
        force_process_exit(1)
    return 0


if __name__ == "__main__":
    main()
