from __future__ import annotations

from typing import Any, Mapping

from .base_handler import BaseGameHandler, GameHandlerCancelled, InstallPlan, InstallPrecheckResult
from .rdr2_handler import Rdr2Handler

_DEFAULT_HANDLER = BaseGameHandler()
_REGISTERED_HANDLERS: tuple[BaseGameHandler, ...] = (
    Rdr2Handler(),
)


def get_game_handler(game_data: Mapping[str, Any] | None = None) -> BaseGameHandler:
    payload = game_data or {}
    for handler in _REGISTERED_HANDLERS:
        if handler.matches(payload):
            return handler
    return _DEFAULT_HANDLER


__all__ = [
    "BaseGameHandler",
    "GameHandlerCancelled",
    "InstallPlan",
    "InstallPrecheckResult",
    "get_game_handler",
]
