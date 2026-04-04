from __future__ import annotations

import logging
import os
from typing import Iterable

from ..common.update_launch import UPDATE_FOREGROUND_ARG


def has_startup_foreground_request(argv: Iterable[str]) -> bool:
    return any(str(token or "").strip().lower() == UPDATE_FOREGROUND_ARG for token in argv)


def request_window_foreground(window, *, logger: logging.Logger | None = None) -> None:
    if os.name != "nt":
        return

    log = logger or logging.getLogger(__name__)
    attempts = (0, 150, 400)

    def _focus_once() -> None:
        try:
            hwnd = int(window.winfo_id())
        except Exception:
            log.debug("Failed to resolve window handle for foreground request", exc_info=True)
            return

        try:
            window.deiconify()
        except Exception:
            log.debug("Failed to deiconify window during foreground request", exc_info=True)

        try:
            window.lift()
        except Exception:
            log.debug("Failed to lift window during foreground request", exc_info=True)

        try:
            window.attributes("-topmost", True)
            window.after(120, lambda: window.attributes("-topmost", False))
        except Exception:
            log.debug("Failed to toggle topmost during foreground request", exc_info=True)

        try:
            window.update_idletasks()
        except Exception:
            log.debug("Failed to flush idle tasks during foreground request", exc_info=True)

        try:
            import ctypes

            user32 = ctypes.windll.user32
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.BringWindowToTop(hwnd)
            user32.SetActiveWindow(hwnd)
            user32.SetFocus(hwnd)
            user32.SetForegroundWindow(hwnd)
        except Exception:
            log.debug("Failed to request Windows foreground focus", exc_info=True)

        try:
            window.focus_force()
        except Exception:
            log.debug("Failed to force focus during foreground request", exc_info=True)

    for delay_ms in attempts:
        try:
            window.after(delay_ms, _focus_once)
        except Exception:
            log.debug("Failed to schedule foreground request", exc_info=True)
            break
