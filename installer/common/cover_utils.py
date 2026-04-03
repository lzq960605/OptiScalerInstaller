from __future__ import annotations

from pathlib import Path


ALLOWED_COVER_IMAGE_EXTENSIONS = frozenset({".webp", ".png", ".jpg"})


def normalize_cover_filename(value: str) -> str:
    raw_name = str(value or "").strip()
    if not raw_name:
        return ""
    if raw_name.lower() in {"null", "none", "na", "n/a", "-"}:
        return ""
    if any(sep in raw_name for sep in ("/", "\\", ":")):
        return ""
    if Path(raw_name).name != raw_name:
        return ""

    suffix = Path(raw_name).suffix.lower()
    if suffix not in ALLOWED_COVER_IMAGE_EXTENSIONS:
        return ""
    return raw_name
