from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import installer_services

_RESHADE_FILE_HINTS = {
    "reshade.ini",
    "reshadepreset.ini",
    "reshade.log",
}
_RESHADE_DIR_HINTS = {
    "reshade-shaders",
}
_RESHADE_PROXY_NAMES = {
    "dxgi.dll",
    "d3d9.dll",
    "d3d10.dll",
    "d3d11.dll",
    "d3d12.dll",
    "opengl32.dll",
}

_SPECIAL_K_FILE_HINTS = {
    "specialk.ini",
    "specialk.log",
    "specialk64.dll",
    "specialk32.dll",
}
_SPECIAL_K_PROXY_NAMES = {
    "dxgi.dll",
    "d3d11.dll",
    "d3d9.dll",
    "dinput8.dll",
}

_ASI_LOADER_PROXY_NAMES = {
    "dinput8.dll",
    "dsound.dll",
    "winmm.dll",
    "version.dll",
}

_GENERIC_PROXY_NAMES = _RESHADE_PROXY_NAMES | _SPECIAL_K_PROXY_NAMES | _ASI_LOADER_PROXY_NAMES

_OWNER_KEYWORDS = {
    "reshade": ("reshade",),
    "specialk": ("special k", "specialk", "kaldaien"),
    "asi_loader": ("ultimate asi loader", "asi loader", "thirteenag"),
}


@dataclass(frozen=True)
class ModConflictFinding:
    kind: str
    evidence: tuple[str, ...]


def _scan_target_entries(target_dir: Path, logger=None) -> tuple[dict[str, Path], set[str]]:
    files: dict[str, Path] = {}
    directories: set[str] = set()
    try:
        for child in target_dir.iterdir():
            lowered_name = child.name.lower()
            if child.is_file():
                files[lowered_name] = child
            elif child.is_dir():
                directories.add(lowered_name)
    except Exception:
        if logger:
            logger.debug("Failed to inspect target directory for common mod conflicts: %s", target_dir, exc_info=True)
    return files, directories


def _is_optiscaler_managed(file_path: Path) -> bool:
    try:
        return bool(installer_services._is_optiscaler_managed_proxy_dll(file_path))
    except Exception:
        return False


def _identify_binary_owner(file_path: Path) -> str:
    if _is_optiscaler_managed(file_path):
        return "optiscaler"

    version_reader = getattr(installer_services, "_read_windows_version_strings", None)
    version_info = version_reader(file_path) if callable(version_reader) else {}
    haystack = " ".join(
        part.lower()
        for part in [file_path.name, *(str(value) for value in version_info.values())]
        if str(part or "").strip()
    )
    for owner, keywords in _OWNER_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return owner
    return ""


def _build_finding(kind: str, evidence: Iterable[str]) -> ModConflictFinding | None:
    normalized = tuple(sorted({str(item).strip() for item in evidence if str(item).strip()}, key=str.lower))
    if not normalized:
        return None
    return ModConflictFinding(kind=kind, evidence=normalized)


def scan_target_mod_conflicts(target_path: str, logger=None) -> tuple[ModConflictFinding, ...]:
    target_dir = Path(str(target_path or "").strip())
    if not target_dir.is_dir():
        return ()

    files, directories = _scan_target_entries(target_dir, logger=logger)
    if not files and not directories:
        return ()

    findings: list[ModConflictFinding] = []
    owner_cache: dict[str, str] = {}
    classified_file_names: set[str] = set()

    def _owner_for(file_name: str) -> str:
        lowered = file_name.lower()
        if lowered not in owner_cache and lowered in files:
            owner_cache[lowered] = _identify_binary_owner(files[lowered])
        return owner_cache.get(lowered, "")

    reshade_hits = {files[name].name for name in _RESHADE_FILE_HINTS if name in files}
    reshade_hits.update("ReShade-Shaders/" for name in _RESHADE_DIR_HINTS if name in directories)
    for dll_name in _RESHADE_PROXY_NAMES:
        if dll_name in files and _owner_for(dll_name) == "reshade":
            reshade_hits.add(files[dll_name].name)
            classified_file_names.add(dll_name)
    finding = _build_finding("reshade", reshade_hits)
    if finding:
        findings.append(finding)

    special_k_hits = {files[name].name for name in _SPECIAL_K_FILE_HINTS if name in files}
    for dll_name in _SPECIAL_K_PROXY_NAMES:
        if dll_name in files and _owner_for(dll_name) == "specialk":
            special_k_hits.add(files[dll_name].name)
            classified_file_names.add(dll_name)
    finding = _build_finding("specialk", special_k_hits)
    if finding:
        findings.append(finding)

    asi_loader_hits = set()
    for dll_name in _ASI_LOADER_PROXY_NAMES:
        if dll_name in files and _owner_for(dll_name) == "asi_loader":
            asi_loader_hits.add(files[dll_name].name)
            classified_file_names.add(dll_name)
    finding = _build_finding("asi_loader", asi_loader_hits)
    if finding:
        findings.append(finding)

    generic_proxy_hits = set()
    for dll_name in _GENERIC_PROXY_NAMES:
        if dll_name not in files or dll_name in classified_file_names:
            continue
        file_path = files[dll_name]
        if _is_optiscaler_managed(file_path):
            continue
        generic_proxy_hits.add(file_path.name)
    finding = _build_finding("proxy_loader", generic_proxy_hits)
    if finding:
        findings.append(finding)

    return tuple(findings)


def _format_finding(finding: ModConflictFinding, use_korean: bool) -> str:
    detected = ", ".join(finding.evidence)
    if finding.kind == "reshade":
        return (
            f"ReShade 관련 파일이 감지되었습니다: {detected}"
            if use_korean
            else f"ReShade-related files were detected: {detected}"
        )
    if finding.kind == "specialk":
        return (
            f"Special K 관련 파일이 감지되었습니다: {detected}"
            if use_korean
            else f"Special K-related files were detected: {detected}"
        )
    if finding.kind == "asi_loader":
        return (
            f"Ultimate ASI Loader 또는 유사 ASI 로더로 보이는 파일이 감지되었습니다: {detected}"
            if use_korean
            else f"Files that look like Ultimate ASI Loader or another ASI loader were detected: {detected}"
        )
    return (
        f"다른 프록시 DLL 또는 로더로 보이는 파일이 감지되었습니다: {detected}"
        if use_korean
        else f"Existing proxy DLLs or loader files were detected: {detected}"
    )


def build_mod_conflict_notice(findings: Iterable[ModConflictFinding], use_korean: bool) -> str:
    normalized_findings = tuple(findings)
    if not normalized_findings:
        return ""

    header = (
        "다른 MOD/로더 흔적이 감지되었습니다. 설치 전에 함께 사용하는 DLL 구성을 확인해 주세요."
        if use_korean
        else "Existing MOD/loader files were detected. Please review the active DLL setup before installing."
    )
    footer = (
        "참고용 알림이며, 같은 프록시 DLL 이름을 사용하는 MOD가 있으면 설치 또는 동작이 충돌할 수 있습니다."
        if use_korean
        else "This is a safety notice. Mods that use the same proxy DLL names can conflict with installation or runtime behavior."
    )

    lines = [header, ""]
    for finding in normalized_findings:
        lines.append(f"- {_format_finding(finding, use_korean)}")
    lines.extend(("", footer))
    return "\n".join(lines).strip()
