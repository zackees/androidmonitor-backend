"""
    app worker
"""

import os
import random
from datetime import datetime
from hmac import compare_digest
from tempfile import TemporaryDirectory

import uvicorn  # type: ignore
from colorama import just_fix_windows_console
from fastapi import FastAPI, File, Header, UploadFile  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles

from androidmonitor_backend.db import (
    DuplicateError,
    db_clear,
    db_get_recent,
    db_insert_uid,
    db_is_token_valid,
    db_try_register,
)
from androidmonitor_backend.log import get_log_reversed, make_logger
from androidmonitor_backend.settings import (
    ALLOW_DB_CLEAR,
    API_ADMIN_KEY,
    CLIENT_API_KEYS,
    CLIENT_TEST_TOKEN,
    URL,
    DB_URL,
    IS_TEST,
    META_UPLOAD_DIR,
    VIDEO_UPLOAD_DIR,
    DOWNLOAD_DIR,
    DOWNLOAD_APK_FILE,
    UPLOAD_DIR
)
from androidmonitor_backend.util import async_download
from androidmonitor_backend.version import VERSION

just_fix_windows_console()

STARTUP_DATETIME = datetime.utcnow()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_UPLOAD_VID_DIR = os.path.join(VIDEO_UPLOAD_DIR, "upload_vid")
TEST_UPLOAD_META_DIR = os.path.join(META_UPLOAD_DIR, "upload_meta")

log = make_logger(__name__)

APP_DISPLAY_NAME = "AndroidMonitor-Backend"

tags_metadata = [
    {
        "name": "admin",
        "description": "Admin control of registering clients",
    },
    {
        "name": "client",
        "description": "Client api",
    },
    {
        "name": "test",
        "description": "Test api",
    },
]

def get_form() -> str:
    """Get form"""
    out: list[str] = []
    return "\n".join(out)


def app_description() -> str:
    """Get the app description."""
    lines = []
    year_str = datetime.utcnow().strftime("%Y")
    lines.append(f"<small>© InternetWatchDogs {year_str}</small>")
    lines.append("## About")
    lines.append("\nHandles user registeration and administration of the AndroidMonitor Network")
    lines.append("## Info")
    lines.append(f"  * Version: `{VERSION}`")
    lines.append("  * Started at: `" + STARTUP_DATETIME.isoformat() + " UTC`")
    if IS_TEST:
        lines.append("  * Running in `TEST` mode")
        lines.append("    * x-api-admin-key: *TEST MODE - NO AUTHENTICATION*")
        lines.append("    * DB_URL: " + f"`{DB_URL}`")
        lines.append("    * ALLOW_DB_CLEAR: " + f"`{ALLOW_DB_CLEAR}`")
        lines.append("    * CLIENT_API_KEYS:")
        for i, client_key in enumerate(CLIENT_API_KEYS):
            lines.append(f"      * `{client_key}`")
        lines.append("    * Quick Links")
        lines.append(f'      * [Register User]({URL}/v1/add_uid)')
    else:
        lines.append("  * Running in PRODUCTION mode")
    lines.append(get_form())
    return "\n".join(lines)


app = FastAPI(
    title=APP_DISPLAY_NAME,
    version=VERSION,
    redoc_url=None,
    description=app_description(),
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if IS_TEST:
    ApiKeyHeader = Header(None)
else:
    ApiKeyHeader = Header(...)


def is_authenticated(api_key: str | None) -> bool:
    """Checks if the request is authenticated."""
    if IS_TEST:
        return True
    if api_key is None:
        return False
    out = compare_digest(api_key, API_ADMIN_KEY)
    if not out:
        log.warning("Invalid API key attempted: %s", api_key)
    return out


def is_client_authenticated(client_api_key: str) -> bool:
    """Checks if the request is authenticated."""
    for client_key in CLIENT_API_KEYS:
        if compare_digest(client_api_key, client_key):
            return True
    return False

app.mount("/download", StaticFiles(directory=DOWNLOAD_DIR, html=True, check_dir=True), name="download")

@app.get("/apk", tags=["client"])
async def apk() -> FileResponse:
    """Get the apk."""
    return FileResponse(DOWNLOAD_APK_FILE, media_type="application/octet-stream", filename="androidmonitor.apk")

@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    """By default redirect to the fastapi docs."""
    return RedirectResponse(url="/docs", status_code=302)


@app.get("/v1/info", tags=["client"])
async def info() -> PlainTextResponse:
    """Get info about the app."""
    lines = []
    lines.append("Version: " + VERSION)
    lines.append("Started at: " + STARTUP_DATETIME.isoformat() + " UTC")
    return PlainTextResponse("\n".join(lines))


def _add_uid() -> tuple[bool, str, str]:
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
        out_rand_str = rand_str[:3] + "-" + rand_str[3:6] + "-" + rand_str[6:]
        now = datetime.utcnow()
        # add it to the database
        try:
            db_insert_uid(rand_str, datetime.utcnow())
            log.info("Added uid %s", rand_str)
            # does the value already exist
            break
        except DuplicateError:
            continue
    return True, out_rand_str, str(now)

@app.get("/v1/add_uid/json", tags=["admin"])
def add_uid(x_api_admin_key: str = ApiKeyHeader) -> JSONResponse:
    """TODO - Add description."""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    ok, uid, created = _add_uid()
    return JSONResponse({"ok": ok, "uid": uid, "created": created})


@app.get("/v1/add_uid", tags=["admin"])
def add_uid_plaintext(x_api_admin_key: str = ApiKeyHeader) -> PlainTextResponse:
    if not is_authenticated(x_api_admin_key):
        return PlainTextResponse('"error": "Invalid API key"', status_code=401)
    ok, uid, created = _add_uid()
    out: str = f"ok: {ok}\nuid: {uid}"
    return PlainTextResponse(out, status_code=200 if ok else 500)



@app.get("/test_headers", tags=["test"])
def test_headers(
    x_data: str = Header(...),
) -> PlainTextResponse:
    """Test the headers."""
    return PlainTextResponse(f"data: {x_data}")


@app.get("/test/download/video", tags=["test"])
def test_download_video() -> FileResponse:
    """Test the download."""
    file = os.path.join(UPLOAD_DIR, "video.mp4")
    return FileResponse(file, media_type="video/mp4", filename="video.mp4")



@app.get("/test/download/meta", tags=["test"])
def test_download_meta() -> FileResponse:
    """Test the download."""
    file = os.path.join(UPLOAD_DIR, "meta.json")
    return FileResponse(file, media_type="text/plain", filename="meta.json")


@app.post("/v1/client_register", tags=["client"])
def register(
    x_uid: str = Header(...), x_client_api_key: str = Header(...)
) -> JSONResponse:
    """Tries to register a device"""
    if not is_authenticated(x_client_api_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    ok, token = db_try_register(x_uid)
    if ok:
        return JSONResponse({"ok": True, "error": None, "token": token})
    return JSONResponse({"ok": False, "error": "Invalid uid", "token": None})


@app.get("/v1/is_client_registered", tags=["client"])
def is_client_registered(
    x_client_token: str = Header(...),
) -> JSONResponse:
    """Checks if a device is registered."""
    return JSONResponse({"is_registered": db_is_token_valid(x_client_token)})


@app.post("/v1/upload", tags=["client"])
async def upload(
    x_client_token: str = Header(...),
    metadata: UploadFile = File(...),
    vidfile: UploadFile = File(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    is_client_test = compare_digest(x_client_token, CLIENT_TEST_TOKEN)
    if is_client_test:
        # this is the test client
        log.info("Test client upload called")
    elif not db_is_token_valid(x_client_token):
        return PlainTextResponse("Invalid client registration", status_code=401)
    if vidfile.filename is None:
        return PlainTextResponse("invalid filename", status_code=400)
    log.info("Upload called with file: %s", vidfile.filename)
    for file in [metadata, vidfile]:
        assert file.filename is not None
        if file == metadata:
            log.info("Metadata file: %s", file.filename)
            temp_path = os.path.join(UPLOAD_DIR, "meta.json")
        else:
            log.info("Video file: %s", file.filename)
            temp_path = os.path.join(UPLOAD_DIR, "video.mp4")
        await async_download(file, temp_path)
        await file.close()
        log.info("Uploaded file %s to %s", file.filename, temp_path)
    return PlainTextResponse(f"Uploaded {metadata.filename} and {vidfile.filename}")


@app.post("/test_upload", tags=["test"])
async def test_upload(
    datafile: UploadFile = File(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    log.info("/test_upload with file: %s", datafile.filename)
    if datafile.filename is None:
        return PlainTextResponse("invalid filename", status_code=400)
    with TemporaryDirectory() as temp_dir:
        temp_datapath: str = os.path.join(temp_dir, datafile.filename)
        await async_download(datafile, temp_datapath)
        log.info("Download test file %s to %s", datafile.filename, temp_datapath)
    return PlainTextResponse(f"Uploaded {datafile.filename} to {temp_datapath}")


@app.get("/get_uids", tags=["admin"])
def log_file(
    x_api_admin_key: str = ApiKeyHeader,
) -> JSONResponse:
    """TODO - Add description."""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    rows = db_get_recent()
    # convert to json
    out = []
    for row in rows:
        json_data = row._asdict()
        for key in json_data:
            # Make values safe for json and add formatting.
            value = json_data[key]
            if key == "uid":
                value = value[:3] + "-" + value[3:6] + "-" + value[6:]
                json_data[key] = value
            elif isinstance(value, datetime):
                json_data[key] = value.isoformat()
        out.append(json_data)
    return JSONResponse(out)


# get the log file
@app.get("/log", tags=["admin"])
def getlog(x_api_admin_key: str = ApiKeyHeader) -> PlainTextResponse:
    """Gets the log file."""
    if not is_authenticated(x_api_admin_key):
        return PlainTextResponse("Invalid API key", status_code=401)
    out = get_log_reversed(100).strip()
    if not out:
        out = "(Empty log file)"
    return PlainTextResponse(out)


if ALLOW_DB_CLEAR:
    # clear database
    @app.delete("/clear", tags=["admin"])
    async def clear(
        delete=False, x_api_admin_key: str = ApiKeyHeader
    ) -> PlainTextResponse:
        """TODO - Add description."""
        if not is_authenticated(x_api_admin_key):
            return PlainTextResponse("Invalid API key", status_code=401)
        log.critical("Clear called")
        db_clear(delete)
        return PlainTextResponse("Deleted all data")


def main() -> None:
    """Start the app."""
    import subprocess  # pylint: disable=import-outside-toplevel
    import webbrowser  # pylint: disable=import-outside-toplevel

    with subprocess.Popen(
        ["supervisord", "-c", "supervisord.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=PROJECT_ROOT,
    ):
        port = 8080
        webbrowser.open(f"http://localhost:{port}")
        uvicorn.run(
            "androidmonitor_backend.app:app", host="localhost", port=port, reload=True
        )


if __name__ == "__main__":
    print(f"Download dir: {DOWNLOAD_DIR}")
    main()
