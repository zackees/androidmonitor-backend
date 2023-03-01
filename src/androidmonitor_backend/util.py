"""
Implements async download
"""
import subprocess
from typing import Any

from fastapi import UploadFile  # type: ignore

from androidmonitor_backend.settings import UPLOAD_CHUNK_SIZE


async def async_download(src: UploadFile, dst: str) -> None:
    """Downloads a file to the destination."""
    with open(dst, mode="wb") as filed:
        while (chunk := await src.read(UPLOAD_CHUNK_SIZE)) != b"":
            filed.write(chunk)
    await src.close()


def check_video(path: str, log: Any) -> None:
    """Checks if the video is valid."""
    try:
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        log.error("Invalid video file: %s", path)
        log.error("Output: %s", exc.stdout)
        log.error("Error: %s", exc.stderr)
        raise
