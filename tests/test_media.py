import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.media import get_ffmpeg_executable


class FfmpegResolutionTests(unittest.TestCase):
    def test_uses_bundled_binary_when_imageio_cannot_resolve_it(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "imageio_ffmpeg"
            binaries = package / "binaries"
            binaries.mkdir(parents=True)
            executable = binaries / "ffmpeg-test.exe"
            executable.touch()
            fake_imageio = types.SimpleNamespace(
                __file__=str(package / "__init__.py"),
                get_ffmpeg_exe=lambda: (_ for _ in ()).throw(RuntimeError("unresolved")),
            )

            with patch("pipeline.media.shutil.which", return_value=None):
                with patch.dict(sys.modules, {"imageio_ffmpeg": fake_imageio}):
                    self.assertEqual(get_ffmpeg_executable(), str(executable))

    def test_prefers_system_ffmpeg(self):
        with patch("pipeline.media.shutil.which", return_value="C:/tools/ffmpeg.exe"):
            self.assertEqual(get_ffmpeg_executable(), "C:/tools/ffmpeg.exe")


if __name__ == "__main__":
    unittest.main()
