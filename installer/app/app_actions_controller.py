from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class AppActionCallbacks:
    show_close_while_installing_warning: Callable[[], None]
    perform_shutdown: Callable[[], None]
    check_for_update: Callable[[Mapping[str, object], bool], bool]


class AppActionsController:
    def __init__(
        self,
        *,
        callbacks: AppActionCallbacks,
    ) -> None:
        self._callbacks = callbacks

    def request_close(self, install_in_progress: bool) -> bool:
        if install_in_progress:
            self._callbacks.show_close_while_installing_warning()
            return False

        self._callbacks.perform_shutdown()
        return True

    def check_app_update(self, module_download_links: Mapping[str, object], *, blocked: bool) -> bool:
        return bool(self._callbacks.check_for_update(module_download_links, bool(blocked)))


__all__ = [
    "AppActionCallbacks",
    "AppActionsController",
]
