from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Executor
from dataclasses import dataclass
import logging
from typing import Any


SchedulerCallback = Callable[[Callable[[], None]], Any]
GameDbLoader = Callable[[str, int], dict[str, dict[str, Any]]]
ModuleLinksLoader = Callable[[str, int], dict[str, Any]]


@dataclass(frozen=True)
class GameDbLoadResult:
    game_db: dict[str, dict[str, Any]]
    module_download_links: dict[str, Any]
    ok: bool
    error: Exception | None
    game_db_gid: int
    game_db_vendor: str


@dataclass(frozen=True)
class GameDbControllerCallbacks:
    on_load_complete: Callable[[GameDbLoadResult], None]


class GameDbLoadController:
    def __init__(
        self,
        *,
        executor: Executor,
        schedule: SchedulerCallback,
        callbacks: GameDbControllerCallbacks,
        spreadsheet_id: str,
        download_links_gid: int,
        load_game_db: GameDbLoader,
        load_module_download_links: ModuleLinksLoader,
        logger=None,
    ) -> None:
        self._executor = executor
        self._schedule = schedule
        self._callbacks = callbacks
        self._spreadsheet_id = str(spreadsheet_id or "")
        self._download_links_gid = int(download_links_gid)
        self._load_game_db = load_game_db
        self._load_module_download_links = load_module_download_links
        self._logger = logger or logging.getLogger()

        self._load_started = False

    def start_load(self, game_db_gid: int, game_db_vendor: str) -> bool:
        if self._load_started:
            return False

        self._load_started = True
        normalized_gid = int(game_db_gid)
        normalized_vendor = str(game_db_vendor or "default")

        try:
            self._executor.submit(self._run_load_worker, normalized_gid, normalized_vendor)
        except Exception as exc:
            self._logger.exception("Failed to submit game DB load worker")
            self._schedule_result(
                GameDbLoadResult(
                    game_db={},
                    module_download_links={},
                    ok=False,
                    error=exc,
                    game_db_gid=normalized_gid,
                    game_db_vendor=normalized_vendor,
                ),
                description="game DB load failure callback",
            )
            return False

        return True

    def _run_load_worker(self, game_db_gid: int, game_db_vendor: str) -> None:
        try:
            game_db = self._load_game_db(self._spreadsheet_id, game_db_gid)
            if not game_db:
                raise ValueError("Sheet has no data.")

            module_links: dict[str, Any] = {}
            try:
                module_links = self._load_module_download_links(self._spreadsheet_id, self._download_links_gid)
            except Exception as link_err:
                self._logger.warning(
                    "Failed to load download-link sheet (gid=%s): %s",
                    self._download_links_gid,
                    link_err,
                )

            result = GameDbLoadResult(
                game_db=game_db,
                module_download_links=module_links,
                ok=True,
                error=None,
                game_db_gid=game_db_gid,
                game_db_vendor=game_db_vendor,
            )
        except Exception as exc:
            result = GameDbLoadResult(
                game_db={},
                module_download_links={},
                ok=False,
                error=exc,
                game_db_gid=game_db_gid,
                game_db_vendor=game_db_vendor,
            )

        self._schedule_result(result, description="game DB load completion callback")

    def _schedule_result(self, result: GameDbLoadResult, *, description: str) -> None:
        try:
            self._schedule(lambda load_result=result: self._callbacks.on_load_complete(load_result))
        except Exception:
            self._logger.exception("Failed to schedule %s", description)
