from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import gpu_notice, message_popup, rtss_notice
from .ui_builder import MainUiTheme


@dataclass(frozen=True)
class AppThemeBundle:
    font_heading: str
    font_ui: str
    install_button_color: str
    install_button_hover_color: str
    install_button_border_color: str
    install_button_disabled_color: str
    install_button_border_disabled_color: str
    install_button_text_color: str
    status_text_color: str
    scan_status_text_color: str
    status_indicator_loading_color: str
    status_indicator_loading_dim_color: str
    status_indicator_online_color: str
    status_indicator_warning_color: str
    status_indicator_offline_color: str
    status_indicator_pulse_ms: int
    link_active_color: str
    link_hover_color: str
    card_background: str
    card_title_overlay_background: str
    card_title_overlay_text: str
    main_ui_theme: MainUiTheme
    rtss_notice_theme: rtss_notice.RtssNoticeTheme
    gpu_notice_theme: gpu_notice.GpuNoticeTheme
    message_popup_theme: message_popup.MessagePopupTheme


def build_app_theme(
    strings: Any,
    *,
    supported_games_wiki_url: str,
    grid_width: int,
    grid_height: int,
) -> AppThemeBundle:
    accent = "#4CC9F0"
    accent_hover = "#35B6E0"
    title_text = "#D6DCE5"
    browse_button = "#5B6574"
    browse_button_hover = "#6A7587"
    popup_ok_button = "#8A95A3"
    popup_ok_button_hover = "#99A4B1"
    install_button = "#D6AA43"
    install_button_hover = "#E2BA58"
    install_button_border = "#F0D082"
    install_button_disabled = "#4B4338"
    install_button_border_disabled = "#5B5246"
    install_button_text = "#0B121A"
    status_text = "#C5CFDB"
    selected_game_highlight = "#FFCB62"
    scan_status_text = "#AEB9C8"
    status_indicator_loading = "#7EE1AA"
    status_indicator_loading_dim = "#415C4D"
    status_indicator_online = "#7EE1AA"
    status_indicator_warning = "#FFCB62"
    status_indicator_offline = "#FF8A8A"
    status_indicator_size = 10
    status_indicator_y_offset = 2
    status_indicator_pulse_ms = 620
    content_side_pad = 20
    meta_right_pad = 5
    scan_meta_right_inset = content_side_pad + meta_right_pad
    link_active = selected_game_highlight
    link_hover = "#FFE08F"
    card_background = "#181B21"
    card_title_overlay_background = "#243447"
    card_title_overlay_text = "#FFFFFF"
    surface = "#2A2E35"
    panel = "#1E2128"
    font_heading = str(strings.main.heading_font_family)
    font_ui = str(strings.main.ui_font_family)

    rtss_notice_theme = rtss_notice.RtssNoticeTheme(
        surface_color=surface,
        accent_color=accent,
        accent_hover_color=accent_hover,
        font_ui=font_ui,
    )
    gpu_notice_theme = gpu_notice.GpuNoticeTheme(
        surface_color=surface,
        accent_color=accent,
        accent_hover_color=accent_hover,
        font_ui=font_ui,
    )
    message_popup_theme = message_popup.MessagePopupTheme(
        surface_color=surface,
        accent_color=popup_ok_button,
        accent_hover_color=popup_ok_button_hover,
        font_ui=font_ui,
    )
    main_ui_theme = MainUiTheme(
        panel_color=panel,
        surface_color=surface,
        title_text_color=title_text,
        font_heading=font_heading,
        font_ui=font_ui,
        status_indicator_size=status_indicator_size,
        status_indicator_loading_color=status_indicator_loading,
        status_indicator_y_offset=status_indicator_y_offset,
        status_text_color=status_text,
        content_side_pad=content_side_pad,
        browse_button_color=browse_button,
        browse_button_hover_color=browse_button_hover,
        scan_status_text_color=scan_status_text,
        scan_meta_right_inset=scan_meta_right_inset,
        supported_games_wiki_url=str(supported_games_wiki_url or ""),
        link_active_color=link_active,
        meta_right_pad=meta_right_pad,
        selected_game_highlight_color=selected_game_highlight,
        grid_width=int(grid_width),
        grid_height=int(grid_height),
        install_button_disabled_color=install_button_disabled,
        install_button_text_color=install_button_text,
        install_button_border_disabled_color=install_button_border_disabled,
    )
    return AppThemeBundle(
        font_heading=font_heading,
        font_ui=font_ui,
        install_button_color=install_button,
        install_button_hover_color=install_button_hover,
        install_button_border_color=install_button_border,
        install_button_disabled_color=install_button_disabled,
        install_button_border_disabled_color=install_button_border_disabled,
        install_button_text_color=install_button_text,
        status_text_color=status_text,
        scan_status_text_color=scan_status_text,
        status_indicator_loading_color=status_indicator_loading,
        status_indicator_loading_dim_color=status_indicator_loading_dim,
        status_indicator_online_color=status_indicator_online,
        status_indicator_warning_color=status_indicator_warning,
        status_indicator_offline_color=status_indicator_offline,
        status_indicator_pulse_ms=status_indicator_pulse_ms,
        link_active_color=link_active,
        link_hover_color=link_hover,
        card_background=card_background,
        card_title_overlay_background=card_title_overlay_background,
        card_title_overlay_text=card_title_overlay_text,
        main_ui_theme=main_ui_theme,
        rtss_notice_theme=rtss_notice_theme,
        gpu_notice_theme=gpu_notice_theme,
        message_popup_theme=message_popup_theme,
    )


__all__ = [
    "AppThemeBundle",
    "build_app_theme",
]
