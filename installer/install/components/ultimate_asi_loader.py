from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse

from .. import services as installer_services


OPTISCALER_ASI_NAME = "OptiScaler.asi"
ULTIMATE_ASI_LOADER_DLL_NAME = "dinput8.dll"
_ULTIMATE_ASI_LOADER_SIGNATURE = "ultimate asi loader"


def _ensure_writable(file_path: Path) -> None:
    try:
        os.chmod(file_path, 0o666)
    except OSError:
        pass


def is_ultimate_asi_loader_dinput8(file_path: Path) -> bool:
    version_info = installer_services.read_windows_version_strings(file_path)
    return any(_ULTIMATE_ASI_LOADER_SIGNATURE in str(value).lower() for value in version_info.values())


def install_ultimate_asi_loader(target_path: str, module_download_links: Mapping[str, object], logger=None) -> None:
    target_dir = Path(str(target_path or "").strip())
    if not target_dir.is_dir():
        raise ValueError(f"Invalid target folder: {target_path}")

    existing_dinput8 = target_dir / ULTIMATE_ASI_LOADER_DLL_NAME
    if existing_dinput8.exists():
        if not existing_dinput8.is_file():
            raise RuntimeError(f"Existing {ULTIMATE_ASI_LOADER_DLL_NAME} is not a file: {existing_dinput8}")
        if not is_ultimate_asi_loader_dinput8(existing_dinput8):
            raise RuntimeError(
                "Existing dinput8.dll does not appear to be Ultimate ASI Loader. "
                "Installation was stopped to avoid overwriting another mod or loader."
            )
        _ensure_writable(existing_dinput8)

    link_entry = module_download_links.get("ultimateasiloader")
    url = ""
    if isinstance(link_entry, dict):
        url = str(link_entry.get("url", "") or "").strip()
    if not url:
        raise FileNotFoundError("Ultimate ASI Loader download link is not configured")

    parsed = urlparse(url)
    archive_name = os.path.basename(parsed.path) or "ultimate_asi_loader.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / archive_name
        extract_path = Path(tmpdir) / "payload"
        installer_services.download_to_file(url, str(archive_path), timeout=60, logger=logger)
        installer_services.extract_archive(str(archive_path), str(extract_path), logger=logger)

        dll_candidates = [
            candidate
            for candidate in extract_path.rglob(ULTIMATE_ASI_LOADER_DLL_NAME)
            if candidate.is_file() and candidate.name.lower() == ULTIMATE_ASI_LOADER_DLL_NAME
        ]
        if not dll_candidates:
            raise FileNotFoundError("dinput8.dll not found inside Ultimate ASI Loader archive")
        if len(dll_candidates) > 1:
            raise RuntimeError("Multiple dinput8.dll files found inside Ultimate ASI Loader archive")

        destination_path = target_dir / ULTIMATE_ASI_LOADER_DLL_NAME
        if destination_path.exists():
            _ensure_writable(destination_path)
        shutil.copy2(dll_candidates[0], destination_path)

    if logger:
        logger.info("Ultimate ASI Loader dinput8.dll installed to %s", destination_path)
