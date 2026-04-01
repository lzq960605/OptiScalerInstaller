from __future__ import annotations

from .base_handler import BaseGameHandler


class Rdr2Handler(BaseGameHandler):
    """Dedicated hook surface for Red Dead Redemption 2 specific install logic."""

    handler_key = "rdr2"
    aliases = (
        "rdr2",
        "red dead redemption 2",
        "red dead redemption ii",
        "playrdr2.exe",
        "rdr2.exe",
    )

