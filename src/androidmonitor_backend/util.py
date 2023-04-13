"""
Implements async download
"""
import subprocess
from datetime import datetime
from typing import Any

import dateutil.parser  # type: ignore
from fastapi import UploadFile  # type: ignore

from androidmonitor_backend.settings import UPLOAD_CHUNK_SIZE


def parse_datetime(date_str: str) -> datetime:
    """Parses a date string."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return dateutil.parser.parse(date_str, fuzzy=True)


async def async_download(src: UploadFile, dst: str, close=True) -> None:
    """Downloads a file to the destination."""
    with open(dst, mode="wb") as filed:
        while (chunk := await src.read(UPLOAD_CHUNK_SIZE)) != b"":
            filed.write(chunk)
    if close:
        await src.close()


async def async_readutf8(src: UploadFile, close=True) -> str:
    """Reads a file as UTF-8."""
    out = b""
    while (chunk := await src.read(UPLOAD_CHUNK_SIZE)) != b"":
        out += chunk
    if close:
        await src.close()
    return out.decode("utf-8")


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
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        err_msg = f"Invalid video file: {path}\n"
        if exc.stdout:
            err_msg += exc.stdout + "\n"
        if exc.stderr:
            err_msg += exc.stderr + "\n"
        log.error(err_msg)
