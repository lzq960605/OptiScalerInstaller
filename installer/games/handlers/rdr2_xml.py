from __future__ import annotations

import os
import stat
import xml.etree.ElementTree as ET
from pathlib import Path


RDR2_SYSTEM_XML_PATH = (
    Path(os.environ.get("USERPROFILE") or str(Path.home()))
    / "Documents"
    / "Rockstar Games"
    / "Red Dead Redemption 2"
    / "Settings"
    / "system.xml"
)


def resolve_rdr2_system_xml_path() -> Path:
    return RDR2_SYSTEM_XML_PATH


def _ensure_child(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    return child


def _ensure_path(root: ET.Element, *tags: str) -> ET.Element:
    node = root
    for tag in tags:
        node = _ensure_child(node, tag)
    return node


def _set_value_attribute(root: ET.Element, path: tuple[str, ...], value: str, logger=None) -> None:
    node = _ensure_path(root, *path)
    previous = node.get("value")
    node.set("value", str(value))
    if logger and previous != str(value):
        logger.info("RDR2 XML edit %s/@value -> %s (was: %s)", "/".join(path), value, previous)


def _set_text_value(root: ET.Element, path: tuple[str, ...], value: str, logger=None) -> None:
    node = _ensure_path(root, *path)
    previous = (node.text or "").strip()
    node.text = str(value)
    if logger and previous != str(value):
        logger.info("RDR2 XML edit %s -> %s (was: %s)", "/".join(path), value, previous)


def apply_rdr2_system_xml_settings(system_xml_path: str | Path | None = None, logger=None) -> Path:
    xml_path = Path(system_xml_path) if system_xml_path else resolve_rdr2_system_xml_path()
    if not xml_path.is_file():
        raise FileNotFoundError(f"RDR2 system.xml not found: {xml_path}")

    original_mode = xml_path.stat().st_mode
    original_readonly = not bool(original_mode & stat.S_IWRITE)

    try:
        if original_readonly:
            os.chmod(xml_path, original_mode | stat.S_IWRITE)
            if logger:
                logger.info("Temporarily removed read-only attribute from %s", xml_path)

        tree = ET.parse(xml_path)
        root = tree.getroot()

        _set_value_attribute(root, ("graphics", "dlssIndex"), "3", logger=logger)
        _set_value_attribute(root, ("graphics", "dlssQuality"), "1", logger=logger)
        _set_value_attribute(root, ("graphics", "fsr2Index"), "0", logger=logger)

        _set_text_value(root, ("advancedGraphics", "API"), "kSettingAPI_DX12", logger=logger)
        _set_value_attribute(root, ("advancedGraphics", "locked"), "false", logger=logger)
        _set_value_attribute(root, ("advancedGraphics", "motionBlur"), "false", logger=logger)

        #_set_value_attribute(root, ("video", "windowed"), "2", logger=logger)
        _set_value_attribute(root, ("video", "tripleBuffered"), "false", logger=logger)
        _set_text_value(root, ("video", "ReflexSettings"), "kSettingReflex_On", logger=logger)

        ET.indent(tree, space="  ")
        tree.write(xml_path, encoding="UTF-8", xml_declaration=True)
        if logger:
            logger.info("Applied RDR2 graphics XML settings to %s", xml_path)
    finally:
        if original_readonly:
            os.chmod(xml_path, original_mode)
            if logger:
                logger.info("Restored read-only attribute on %s", xml_path)

    return xml_path
