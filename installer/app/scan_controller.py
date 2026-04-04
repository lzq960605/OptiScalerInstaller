from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import Executor
from dataclasses import dataclass
import logging
from typing import Any

from ..games import scanner as game_scanner
from ..i18n import Lang


GameDbProvider = Callable[[], dict[str, dict[str, Any]]]
LangProvider = Callable[[], Lang]
GameSupportPredicate = Callable[[dict[str, Any]], bool]
SchedulerCallback = Callable[[Callable[[], None]], Any]


@dataclass(frozen=True)
class ScanControllerCallbacks:
    prepare_scan_ui: Callable[[], None]
    reset_scan_results: Callable[[], None]
    add_game_card: Callable[[dict[str, Any]], None]
    finish_scan_ui: Callable[[], None]
    pump_poster_queue: Callable[[], None]
    show_auto_scan_empty_popup: Callable[[], None]
    show_manual_scan_empty_popup: Callable[[], None]
    show_select_game_hint: Callable[[], None]


class ScanController:
    def __init__(
        self,
        *,
        executor: Executor,
        schedule: SchedulerCallback,
        callbacks: ScanControllerCallbacks,
        get_game_db: GameDbProvider,
        get_lang: LangProvider,
        is_game_supported: GameSupportPredicate,
        logger=None,
    ) -> None:
        self._executor = executor
        self._schedule = schedule
        self._callbacks = callbacks
        self._get_game_db = get_game_db
        self._get_lang = get_lang
        self._is_game_supported = is_game_supported
        self._logger = logger or logging.getLogger()

        self._scan_in_progress = False
        self._auto_scan_active = False
        self._scan_generation = 0
        self._found_count = 0

    @property
    def is_scan_in_progress(self) -> bool:
        return self._scan_in_progress

    def start_auto_scan(self) -> bool:
        if self._scan_in_progress:
            return False

        scan_paths = game_scanner.get_auto_scan_paths(logger=self._logger)
        if not scan_paths:
            self._callbacks.show_auto_scan_empty_popup()
            return False

        return self.start_scan(scan_paths, is_auto=True)

    def start_manual_scan(self, folder_path: str) -> bool:
        normalized_path = str(folder_path or "").strip()
        if not normalized_path or self._scan_in_progress:
            return False
        return self.start_scan([normalized_path], is_auto=False)

    def start_scan(self, scan_paths: Iterable[str], *, is_auto: bool) -> bool:
        normalized_paths = [str(path or "").strip() for path in scan_paths if str(path or "").strip()]
        if not normalized_paths or self._scan_in_progress:
            return False

        self._scan_generation += 1
        generation = self._scan_generation
        self._scan_in_progress = True
        self._auto_scan_active = bool(is_auto)
        self._found_count = 0

        self._callbacks.reset_scan_results()
        self._callbacks.prepare_scan_ui()

        try:
            self._executor.submit(
                self._run_scan_worker,
                generation,
                tuple(normalized_paths),
                dict(self._get_game_db() or {}),
                self._get_lang(),
            )
        except Exception:
            self._logger.exception("Failed to submit scan worker")
            self._scan_in_progress = False
            self._auto_scan_active = False
            self._callbacks.finish_scan_ui()
            self._callbacks.pump_poster_queue()
            return False

        return True

    def _run_scan_worker(
        self,
        generation: int,
        scan_paths: tuple[str, ...],
        game_db: dict[str, dict[str, Any]],
        lang: Lang,
    ) -> None:
        try:
            for game in game_scanner.iter_scan_game_folders(
                scan_paths,
                game_db,
                lang=lang,
                is_game_supported=self._is_game_supported,
                logger=self._logger,
            ):
                self._schedule_callback(
                    lambda game_record=game, scheduled_generation=generation: self._on_game_found(
                        scheduled_generation,
                        game_record,
                    ),
                    description="found-game callback",
                )
        except Exception:
            self._logger.exception("Scan worker error")
        finally:
            self._schedule_callback(
                lambda scheduled_generation=generation: self._on_scan_complete(scheduled_generation),
                description="scan completion callback",
            )

    def _schedule_callback(self, callback: Callable[[], None], *, description: str) -> None:
        try:
            self._schedule(callback)
        except Exception:
            self._logger.exception("Failed to schedule %s", description)

    def _on_game_found(self, generation: int, game: dict[str, Any]) -> None:
        if generation != self._scan_generation:
            return

        self._found_count += 1
        self._callbacks.add_game_card(game)

    def _on_scan_complete(self, generation: int) -> None:
        if generation != self._scan_generation:
            return

        was_auto = self._auto_scan_active
        self._scan_in_progress = False
        self._auto_scan_active = False

        self._callbacks.finish_scan_ui()

        if self._found_count > 0:
            self._callbacks.show_select_game_hint()
        elif was_auto:
            self._callbacks.show_auto_scan_empty_popup()
        else:
            self._callbacks.show_manual_scan_empty_popup()

        self._callbacks.pump_poster_queue()
