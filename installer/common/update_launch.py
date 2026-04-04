from __future__ import annotations

import os
from pathlib import Path


UPDATE_FOREGROUND_ARG = "--foreground-after-update"


def build_updated_installer_launch_command(target: str | Path) -> list[str]:
    command = [str(Path(target))]
    if os.name == "nt":
        command.append(UPDATE_FOREGROUND_ARG)
    return command
