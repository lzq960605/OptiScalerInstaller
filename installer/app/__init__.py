"""UI and application-facing helpers."""

from . import gpu_notice, rtss_notice
from .popup_markup import (
    create_popup_markup_text,
    estimate_wrapped_text_lines,
    render_markup_to_text_widget,
    strip_markup_text,
)
from .popup_utils import PopupFadeController, create_modal_popup, present_modal_popup

__all__ = [
    "PopupFadeController",
    "create_modal_popup",
    "create_popup_markup_text",
    "estimate_wrapped_text_lines",
    "gpu_notice",
    "present_modal_popup",
    "render_markup_to_text_widget",
    "rtss_notice",
    "strip_markup_text",
]
