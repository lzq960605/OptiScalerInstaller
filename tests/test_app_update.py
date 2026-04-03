from __future__ import annotations

from pathlib import Path
import unittest
from unittest import mock

from installer import app_update


class AppUpdateTests(unittest.TestCase):
    def test_parse_version_tuple_extracts_numeric_parts(self) -> None:
        self.assertEqual(app_update.parse_version_tuple("v0.2.4-beta.1"), (0, 2, 4, 1))

    def test_build_expected_installer_exe_name_uses_version_text(self) -> None:
        self.assertEqual(
            app_update.build_expected_installer_exe_name("v0.2.5"),
            "OptiScaler_Installer_v0.2.5.exe",
        )

    def test_resolve_safe_child_path_blocks_escape_attempts(self) -> None:
        base_dir = Path("C:/workspace/base")
        self.assertIsNone(app_update.resolve_safe_child_path(base_dir, "..\\escape.exe"))
        self.assertEqual(
            app_update.resolve_safe_child_path(base_dir, "nested/file.exe"),
            (base_dir / "nested" / "file.exe").resolve(strict=False),
        )

    def test_get_installer_update_entry_returns_only_mapping_entries(self) -> None:
        self.assertEqual(
            app_update.get_installer_update_entry({"latest_installer_dl": {"version": "0.2.5"}}),
            {"version": "0.2.5"},
        )
        self.assertEqual(app_update.get_installer_update_entry({"latest_installer_dl": "0.2.5"}), {})

    def test_prepare_installer_update_payload_renames_downloaded_exe(self) -> None:
        payload_path = Path("C:/workspace/installer.exe")
        expected = Path("C:/workspace/OptiScaler_Installer_v0.2.5.exe")

        with mock.patch.object(Path, "exists", autospec=True, return_value=False), mock.patch.object(
            Path,
            "replace",
            autospec=True,
            return_value=expected,
        ) as replace_mock:
            launch_path = app_update.prepare_installer_update_payload(
                payload_path,
                Path("C:/workspace"),
                "0.2.5",
            )

        self.assertEqual(launch_path, expected)
        replace_mock.assert_called_once_with(payload_path, expected)

    def test_prepare_installer_update_payload_extracts_expected_zip_exe(self) -> None:
        payload_path = Path("C:/workspace/update.zip")
        target_dir = Path("C:/workspace/extracted")
        expected = target_dir / "nested" / "OptiScaler_Installer_v0.2.5.exe"
        zip_member = mock.Mock()
        zip_member.is_dir.return_value = False
        zip_member.filename = "nested/OptiScaler_Installer_v0.2.5.exe"
        zip_context = mock.MagicMock()
        zip_context.__enter__.return_value.infolist.return_value = [zip_member]

        with mock.patch("installer.app_update.zipfile.ZipFile", return_value=zip_context), mock.patch(
            "installer.app_update.installer_services.extract_archive"
        ) as extract_archive_mock, mock.patch(
            "installer.app_update.resolve_safe_child_path",
            return_value=expected,
        ) as resolve_mock, mock.patch.object(
            Path,
            "exists",
            autospec=True,
            side_effect=lambda self: self == expected,
        ), mock.patch.object(
            Path,
            "unlink",
            autospec=True,
        ) as unlink_mock:
            launch_path = app_update.prepare_installer_update_payload(
                payload_path,
                target_dir,
                "0.2.5",
            )

        self.assertEqual(launch_path, expected)
        extract_archive_mock.assert_called_once_with(str(payload_path), str(target_dir))
        resolve_mock.assert_called_once_with(target_dir, zip_member.filename)
        unlink_mock.assert_called_once_with(payload_path, missing_ok=True)


if __name__ == "__main__":
    unittest.main()
