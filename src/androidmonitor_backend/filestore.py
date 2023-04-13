"""Abstraction for file I/O."""

import os
import shutil
import tempfile

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse

from androidmonitor_backend.s3 import s3_download


def is_s3(uri: str) -> bool:
    """Return True if the given uri is an s3:// uri."""
    return "s3://" in uri


def create_download_response(
    uri: str, media_type: str, filename: str | None = None
) -> FileResponse:
    """Create a FileResponse for the given uri. Either s3:// or a local file path."""
    filename = filename or os.path.basename(uri)
    if not is_s3(uri):
        return FileResponse(uri, media_type=media_type)
    tmpfile = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
        delete=False
    )
    tmpfile.close()
    s3_download(uri, tmpfile.name)
    bg_tasks = BackgroundTasks()
    bg_tasks.add_task(lambda: os.remove(tmpfile.name))
    return FileResponse(filename, media_type=media_type, background=bg_tasks)


def fetch(uri: str) -> bytes | Exception:
    """Fetch a file from the given uri and return its contents as a string."""
    if not is_s3(uri):
        with open(uri, mode="rb") as file:
            return file.read()
    tmpfile = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
        delete=False
    )
    tmpfile.close()
    exception = s3_download(uri, tmpfile.name)
    if exception:
        return exception
    with open(tmpfile.name, mode="rb") as file:
        return file.read()


def copy(uri: str, destination: str) -> Exception | None:
    """Copy a file from the given uri to the given destination."""
    if not is_s3(uri):
        shutil.copyfile(uri, destination)
        return None
    exception = s3_download(uri, destination)
    if exception:
        return exception
    return None
