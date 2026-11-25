from pathlib import Path
import shutil


def get_ffmpeg_executable():
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    try:
        import imageio_ffmpeg
    except ImportError as error:
        raise RuntimeError(
            "FFmpeg is unavailable. Install FFmpeg on PATH or install project requirements "
            "with the active Python environment."
        ) from error

    try:
        bundled_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except RuntimeError:
        bundled_ffmpeg = None
    if bundled_ffmpeg and Path(bundled_ffmpeg).is_file():
        return bundled_ffmpeg

    binary_dir = Path(imageio_ffmpeg.__file__).resolve().parent / "binaries"
    bundled_candidates = sorted(path for path in binary_dir.glob("ffmpeg*") if path.is_file())
    if bundled_candidates:
        return str(bundled_candidates[0])

    raise RuntimeError(
        "No FFmpeg executable was found. Install FFmpeg and add it to PATH, or reinstall "
        "imageio-ffmpeg in the active environment with "
        "`python -m pip install --force-reinstall imageio-ffmpeg`."
    )
