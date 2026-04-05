"""Shared low-level infrastructure helpers."""

import logging
from collections.abc import Callable

from .network_utils import get_shared_retry_session
from .process_utils import subprocess_no_window_kwargs


def schedule_safely(
    schedule_fn: Callable[[Callable[[], None]], object],
    callback: Callable[[], None],
    logger: logging.Logger,
    *,
    description: str,
) -> None:
    try:
        schedule_fn(callback)
    except Exception:
        logger.exception("Failed to schedule %s", description)


__all__ = [
    "get_shared_retry_session",
    "schedule_safely",
    "subprocess_no_window_kwargs",
]
