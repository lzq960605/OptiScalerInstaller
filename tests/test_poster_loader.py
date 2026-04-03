from __future__ import annotations

from pathlib import Path
import shutil
import unittest
import uuid
from unittest import mock

from PIL import Image

from installer.common.cover_utils import normalize_cover_filename
from installer.common.poster_loader import PosterImageLoader, PosterLoaderConfig


TEST_ROOT = Path(__file__).resolve().parents[1]
TEST_RUNTIME_ROOT = TEST_ROOT / "tests_runtime"


class PosterLoaderTests(unittest.TestCase):
    def _make_test_root(self) -> Path:
        root_dir = TEST_RUNTIME_ROOT / uuid.uuid4().hex
        root_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root_dir, ignore_errors=True))
        return root_dir

    def _build_loader(self, root_dir: Path, **overrides) -> PosterImageLoader:
        assets_dir = root_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        config = PosterLoaderConfig(
            cache_dir=root_dir / "cache",
            assets_dir=assets_dir,
            default_poster_candidates=(assets_dir / "default_poster.png",),
            target_width=120,
            target_height=180,
            **overrides,
        )
        return PosterImageLoader(config)

    def test_normalize_cover_filename_rejects_paths_and_invalid_extensions(self) -> None:
        self.assertEqual(normalize_cover_filename("poster.webp"), "poster.webp")
        self.assertEqual(normalize_cover_filename("folder/poster.webp"), "")
        self.assertEqual(normalize_cover_filename("poster.gif"), "")
        self.assertEqual(normalize_cover_filename("none"), "")

    def test_load_uses_cached_cover_file_when_present(self) -> None:
        root_dir = self._make_test_root()
        loader = self._build_loader(root_dir)
        cache_path = root_dir / "cache" / "poster.png"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (30, 60), "#335577").save(cache_path, format="PNG")

        try:
            result = loader.load("Sample Game", "poster.png", "https://example.com/poster.png")
        finally:
            loader.close()

        self.assertFalse(result.is_default)
        self.assertFalse(result.should_retry)
        self.assertEqual(result.image.size, (120, 180))

    def test_load_returns_default_and_retry_flag_when_remote_download_fails(self) -> None:
        root_dir = self._make_test_root()
        loader = self._build_loader(root_dir)

        try:
            with mock.patch.object(loader, "_download_image_bytes", side_effect=RuntimeError("boom")):
                result = loader.load("Sample Game", "", "https://example.com/poster.png")
        finally:
            loader.close()

        self.assertTrue(result.is_default)
        self.assertTrue(result.should_retry)
        self.assertEqual(result.image.size, (120, 180))


if __name__ == "__main__":
    unittest.main()
