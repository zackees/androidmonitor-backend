"""
    app worker
"""

import os
import random
from datetime import datetime
from tempfile import TemporaryDirectory
import uvicorn  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse
from fastapi import FastAPI, UploadFile, File  # type: ignore
from colorama import just_fix_windows_console

from androidmonitor_backend.util import async_download
from androidmonitor_backend.log import make_logger, get_log_reversed
from androidmonitor_backend.version import VERSION
from androidmonitor_backend.db import db_get_recent, db_insert_uuid, db_clear, DuplicateError
from androidmonitor_backend.settings import IS_TEST

just_fix_windows_console()

STARTUP_DATETIME = datetime.utcnow()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = make_logger(__name__)

APP_DISPLAY_NAME = "AndroidMonitor-Backend"


def app_description() -> str:
    """Get the app description."""
    lines = []
    lines.append("  * Version: " + VERSION)
    lines.append("  * Started at: " + STARTUP_DATETIME.isoformat() + " UTC")
    if IS_TEST:
        lines.append("  * Running in TEST mode")
    else:
        lines.append("  * Running in PRODUCTION mode")
    return "\n".join(lines)


app = FastAPI(
    title=APP_DISPLAY_NAME,
    version=VERSION,
    redoc_url=None,
    license_info={
        "name": "Handles all the backend stuff for AndroidMonitor",
    },
    description=app_description(),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    """By default redirect to the fastapi docs."""
    return RedirectResponse(url="/docs", status_code=302)


@app.get("/get_uuids")
def log_file() -> JSONResponse:
    """TODO - Add description."""
    rows = db_get_recent()
    # convert to json
    out = []
    for row in rows:
        json_data = row._asdict()
        for key in json_data:
            value = json_data[key]
            if isinstance(value, datetime):
                json_data[key] = value.isoformat()
        out.append(json_data)
    return JSONResponse(out)


# add uuid
@app.post("/add_uuid")
def add_uuid() -> JSONResponse:
    """TODO - Add description."""
    while True:
        # generate a random 8 digit number
        random_value = random.randint(0, 99999999)
        rand_str = str(random_value).zfill(8)
        # sum all digits and add the last digit as the checksum
        total = 0
        for char in rand_str:
            total += int(char)
        total = total % 10
        rand_str += str(total)
        # insert a - in the middle
        rand_str = rand_str[:3] + "-" + rand_str[3:6] + "-" + rand_str[6:]
        now = datetime.utcnow()
        # add it to the database
        try:
            db_insert_uuid(rand_str, datetime.utcnow())
            log.info("Added uuid %s", rand_str)
            # does the value already exist
            break
        except DuplicateError:
            continue
    return JSONResponse({"ok": True, "uuid": rand_str, "created": str(now)})


# get the log file
@app.get("/log")
def getlog() -> PlainTextResponse:
    """Gets the log file."""
    out = get_log_reversed(100).strip()
    if not out:
        out = "(Empty log file)"
    return PlainTextResponse(out)


@app.post("/upload")
async def upload(
    datafile: UploadFile = File(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    log.info("Upload called with file: %s", datafile.filename)
    with TemporaryDirectory() as temp_dir:
        temp_datapath: str = os.path.join(temp_dir, datafile.filename)
        await async_download(datafile, temp_datapath)
        await datafile.close()
        log.info("Downloaded file %s to %s", datafile.filename, temp_datapath)
        # shutil.move(temp_path, final_path)
    return PlainTextResponse(f"Uploaded {datafile.filename} to {temp_datapath}")


if IS_TEST:
    # clear database
    @app.delete("/clear")
    async def clear() -> PlainTextResponse:
        """TODO - Add description."""
        log.critical("Clear called")
        db_clear()
        return PlainTextResponse("Deleted all data")


def main() -> None:
    """Start the app."""
    import webbrowser  # pylint: disable=import-outside-toplevel

    webbrowser.open("http://localhost:8080")
    uvicorn.run(app, host="localhost", port=8080)


if __name__ == "__main__":
    main()
