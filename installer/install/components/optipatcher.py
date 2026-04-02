from __future__ import annotations

from typing import Mapping

from .. import services as installer_services


def install_optipatcher(
    target_path: str,
    game_data: Mapping[str, object],
    module_download_links: Mapping[str, object],
    default_url: str,
    logger=None,
) -> dict[str, str]:
    if not bool(game_data.get("optipatcher")):
        return {}

    module_key = str(game_data.get("module_dl", "")).strip().lower()
    opti_key = module_key or "optipatcher"
    opti_link_entry = module_download_links.get(opti_key) or module_download_links.get("optipatcher")
    opti_url = str(default_url or "").strip()
    if isinstance(opti_link_entry, dict):
        opti_url = str(opti_link_entry.get("url", opti_url) or opti_url).strip()

    installer_services.install_optipatcher(target_path, url=opti_url, logger=logger)
    if logger:
        logger.info("Installed OptiPatcher from %s to %s", opti_url, target_path)
    return {"LoadAsiPlugins": "True"}
