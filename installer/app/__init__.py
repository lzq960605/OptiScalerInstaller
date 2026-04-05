"""UI and application-facing helpers."""

from . import gpu_notice, message_popup, rtss_notice
from .archive_controller import ArchivePreparationCallbacks, ArchivePreparationController, ArchivePreparationState
from .app_actions_controller import AppActionCallbacks, AppActionsController
from .app_shutdown_controller import AppShutdownCallbacks, AppShutdownController, AppShutdownStep
from .card_factory import GameCardBuildResult, GameCardTheme, create_game_card
from .card_ui import GameCardUiCallbacks, GameCardUiController
from .card_layout import (
    CardOverflowFitDecision,
    CardResizeReflowDecision,
    compute_card_overflow_fit_decision,
    compute_card_resize_reflow_decision,
)
from .card_viewport import CardViewportCallbacks, CardViewportController, CardViewportRuntime
from .card_render_controller import CardRenderCallbacks, CardRenderController
from .controller_factory import AppControllerFactoryConfig, AppControllers, bind_app_controllers, build_app_controllers
from .card_grid import (
    CardGridPlacement,
    build_card_grid_placements,
    clamp_grid_columns,
    compute_visible_game_indices,
    get_card_grid_placement,
)
from .card_visuals import (
    GameCardVisualTheme,
    ensure_game_card_image_cache,
    render_game_card_visual,
    update_game_card_base_image,
)
from .game_db_controller import GameDbControllerCallbacks, GameDbLoadController, GameDbLoadResult
from .gpu_flow_controller import GpuFlowCallbacks, GpuFlowController, GpuFlowState
from .install_selection_controller import (
    InstallSelectionCallbacks,
    InstallSelectionController,
    InstallSelectionPrecheckOutcome,
    InstallSelectionUiState,
)
from .install_state import (
    SelectedGameSnapshot,
    build_install_button_state_inputs,
    build_install_entry_state,
    build_selected_game_snapshot,
)
from .install_flow import InstallFlowCallbacks, InstallFlowController, create_install_flow_controller
from .install_ui_state import InstallButtonState, InstallButtonStateInputs, compute_install_button_state
from .install_entry import InstallEntryDecision, InstallEntryState, validate_install_entry
from .message_popup import MessagePopupTheme, show_message_popup
from .notice_controller import AppNoticeController
from .popup_markup import (
    create_popup_markup_text,
    estimate_wrapped_text_lines,
    render_markup_to_text_widget,
    strip_markup_text,
)
from .popup_utils import PopupFadeController, create_modal_popup, present_modal_popup
from .runtime_state import (
    ArchiveRuntimeState,
    CardUiRuntimeState,
    GpuRuntimeState,
    InstallRuntimeState,
    RuntimeStateBundle,
    SheetRuntimeState,
    build_runtime_state_bundle,
    get_runtime_state_attr,
    set_runtime_state_attr,
)
from .scan_feedback import ScanFeedbackCallbacks, ScanFeedbackController
from .scan_entry_controller import ScanEntryCallbacks, ScanEntryController, ScanEntryState
from .scan_controller import ScanController, ScanControllerCallbacks
from .startup_flow import StartupFlowController, StartupFlowCallbacks
from .startup_window import (
    StartupWindowLayout,
    apply_startup_window_layout,
    apply_startup_window_workaround,
    build_centered_window_geometry,
    build_startup_window_layout,
    get_ctk_scale,
    get_umpc_startup_window_size,
    is_windows_slate_mode,
    resolve_startup_poster_target_size,
    should_apply_umpc_window_workaround,
)
from .theme import AppThemeBundle, build_app_theme
from .ui_presenters import BottomPanelPresenter, HeaderStatusPresenter

__all__ = [
    "ArchivePreparationCallbacks",
    "ArchivePreparationController",
    "ArchivePreparationState",
    "AppNoticeController",
    "AppActionCallbacks",
    "AppActionsController",
    "AppShutdownCallbacks",
    "AppShutdownController",
    "AppShutdownStep",
    "AppThemeBundle",
    "ArchiveRuntimeState",
    "BottomPanelPresenter",
    "CardUiRuntimeState",
    "CardOverflowFitDecision",
    "CardRenderCallbacks",
    "CardRenderController",
    "CardResizeReflowDecision",
    "AppControllerFactoryConfig",
    "AppControllers",
    "CardViewportCallbacks",
    "CardViewportController",
    "CardViewportRuntime",
    "GameCardBuildResult",
    "GameCardUiCallbacks",
    "GameCardUiController",
    "GameCardTheme",
    "GameCardVisualTheme",
    "CardGridPlacement",
    "GameDbControllerCallbacks",
    "GameDbLoadController",
    "GameDbLoadResult",
    "GpuFlowCallbacks",
    "GpuFlowController",
    "GpuFlowState",
    "GpuRuntimeState",
    "InstallEntryDecision",
    "InstallEntryState",
    "InstallFlowCallbacks",
    "InstallFlowController",
    "InstallButtonState",
    "InstallButtonStateInputs",
    "InstallRuntimeState",
    "InstallSelectionCallbacks",
    "InstallSelectionController",
    "InstallSelectionPrecheckOutcome",
    "InstallSelectionUiState",
    "SelectedGameSnapshot",
    "MessagePopupTheme",
    "PopupFadeController",
    "ScanController",
    "ScanControllerCallbacks",
    "ScanEntryCallbacks",
    "ScanEntryController",
    "ScanEntryState",
    "ScanFeedbackCallbacks",
    "ScanFeedbackController",
    "SheetRuntimeState",
    "StartupFlowController",
    "StartupFlowCallbacks",
    "StartupWindowLayout",
    "RuntimeStateBundle",
    "HeaderStatusPresenter",
    "apply_startup_window_layout",
    "apply_startup_window_workaround",
    "build_centered_window_geometry",
    "build_runtime_state_bundle",
    "build_app_theme",
    "build_startup_window_layout",
    "create_modal_popup",
    "create_popup_markup_text",
    "get_runtime_state_attr",
    "get_ctk_scale",
    "get_umpc_startup_window_size",
    "estimate_wrapped_text_lines",
    "gpu_notice",
    "message_popup",
    "build_install_button_state_inputs",
    "build_install_entry_state",
    "create_install_flow_controller",
    "build_selected_game_snapshot",
    "create_game_card",
    "compute_card_overflow_fit_decision",
    "compute_card_resize_reflow_decision",
    "build_card_grid_placements",
    "bind_app_controllers",
    "build_app_controllers",
    "clamp_grid_columns",
    "compute_visible_game_indices",
    "ensure_game_card_image_cache",
    "present_modal_popup",
    "compute_install_button_state",
    "get_card_grid_placement",
    "render_game_card_visual",
    "render_markup_to_text_widget",
    "rtss_notice",
    "show_message_popup",
    "is_windows_slate_mode",
    "resolve_startup_poster_target_size",
    "set_runtime_state_attr",
    "strip_markup_text",
    "should_apply_umpc_window_workaround",
    "update_game_card_base_image",
    "validate_install_entry",
]
