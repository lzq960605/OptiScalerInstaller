from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

if os.name == "nt":
    import winreg


def _log_info_if_logger(logger: Any, message: str, *args) -> None:
    if logger:
        logger.info(message, *args)
    else:
        logging.info(message, *args)


def _log_warning(logger: Any, message: str, *args) -> None:
    if logger:
        logger.warning(message, *args)
    else:
        logging.warning(message, *args)


def _get_rtss_install_path() -> Path:
    if os.name == "nt":
        roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        subkeys = [r"SOFTWARE\WOW6432Node\Unwinder\RTSS", r"SOFTWARE\Unwinder\RTSS"]

        for root in roots:
            for subkey in subkeys:
                try:
                    with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as key:
                        val, _ = winreg.QueryValueEx(key, "InstallPath")
                        if val:
                            path = Path(val)
                            if path.is_file() and path.name.lower() == "rtss.exe":
                                path = path.parent
                            if path.exists():
                                return path
                except Exception:
                    continue

    return Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "RivaTuner Statistics Server"


def _read_rtss_global_settings(global_path: Path) -> tuple[Optional[str], Optional[str]]:
    ref_val, detours_val = None, None
    lines = global_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    for line in lines:
        line = line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip()
        if normalized_key == "ReflexSetLatencyMarker":
            ref_val = normalized_value
        elif normalized_key == "UseDetours":
            detours_val = normalized_value
    return ref_val, detours_val


def _is_rtss_config_ok(ref_val: Optional[str], detours_val: Optional[str]) -> bool:
    return ref_val == "0" and detours_val == "1"


def _write_rtss_global_settings(global_path: Path, logger: Any = None) -> None:
    target_keys = {
        "ReflexSetLatencyMarker": "0",
        "UseDetours": "1",
    }

    raw_bytes = global_path.read_bytes()
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    content_bytes = raw_bytes[3:] if has_bom else raw_bytes

    if b"\r\n" in content_bytes:
        line_ending = "\r\n"
    elif b"\r" in content_bytes:
        line_ending = "\r"
    else:
        line_ending = "\n"

    text = content_bytes.decode("utf-8", errors="ignore")
    lines = text.splitlines()

    new_lines = []
    applied_keys: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if "=" in stripped:
            key, _ = stripped.split("=", 1)
            key = key.strip()
            if key in target_keys:
                new_lines.append(f"{key}={target_keys[key]}")
                applied_keys.add(key)
                continue
        new_lines.append(line)

    for key, value in target_keys.items():
        if key not in applied_keys:
            new_lines.append(f"{key}={value}")
            _log_info_if_logger(logger, "[RTSS] Key not found in Global file, appending: %s=%s", key, value)

    new_text = line_ending.join(new_lines)
    if text.endswith("\n") or text.endswith("\r"):
        new_text += line_ending

    encoded = new_text.encode("utf-8")
    if has_bom:
        encoded = b"\xef\xbb\xbf" + encoded

    global_path.write_bytes(encoded)
    _log_info_if_logger(logger, "[RTSS] Global file updated: %s", global_path)


def apply_rtss_global_settings_if_needed(logger: Any = None) -> None:
    """Called after a successful install. Silently fixes RTSS Global settings if needed.
    No popup is shown. Read-only state of the file is preserved."""
    try:
        install_path = _get_rtss_install_path()
        global_path = install_path / "Profiles" / "Global"

        if not global_path.exists():
            _log_info_if_logger(logger, "[RTSS] Global file not found, skipping fix: %s", global_path)
            return

        ref_val, detours_val = _read_rtss_global_settings(global_path)
        _log_info_if_logger(
            logger,
            "[RTSS] Pre-fix values: ReflexSetLatencyMarker=%s, UseDetours=%s",
            ref_val,
            detours_val,
        )

        if _is_rtss_config_ok(ref_val, detours_val):
            _log_info_if_logger(logger, "[RTSS] Settings already OK, no changes needed")
            return

        import stat as _stat
        orig_stat = global_path.stat()
        orig_readonly = not (orig_stat.st_mode & _stat.S_IWRITE)

        try:
            if orig_readonly:
                global_path.chmod(orig_stat.st_mode | _stat.S_IWRITE)
                _log_info_if_logger(logger, "[RTSS] Temporarily removed read-only from Global file")

            _write_rtss_global_settings(global_path, logger=logger)
        finally:
            if orig_readonly:
                global_path.chmod(orig_stat.st_mode & ~_stat.S_IWRITE)
                _log_info_if_logger(logger, "[RTSS] Restored read-only on Global file")

    except Exception as exc:
        _log_warning(logger, "[RTSS] Failed to apply Global settings fix: %s", exc)
