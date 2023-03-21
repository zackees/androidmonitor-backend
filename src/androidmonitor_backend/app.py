"""
    app worker
"""

# pylint: disable=redefined-builtin

import json
import os
from datetime import datetime
from hmac import compare_digest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from zipfile import ZipFile

import colorama  # pylint: disable=no-name-in-module
import uvicorn  # type: ignore
from fastapi import Form  # type: ignore
from fastapi import BackgroundTasks, FastAPI, File, Header, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles

from androidmonitor_backend.db import (
    VideoItem,
    db_add_log,
    db_add_uid,
    db_clear,
    db_get_log,
    db_get_recent,
    db_get_recent_logs_ids,
    db_get_recent_videos,
    db_get_uploads,
    db_get_user_from_token,
    db_get_video,
    db_is_token_valid,
    db_list_logs,
    db_register_upload,
    db_try_register,
)
from androidmonitor_backend.log import get_log_reversed, make_logger
from androidmonitor_backend.settings import ALLOW_DB_CLEAR  # UPLOAD_DIR,
from androidmonitor_backend.settings import (
    API_ADMIN_KEY,
    APK_UPDATE_FILE,
    CLIENT_API_KEYS,
    CLIENT_TEST_TOKEN,
    DB_URL,
    DOWNLOAD_APK_FILE,
    IS_TEST,
    UPLOAD_DIR,
    URL,
    WWW_DIR,
)
from androidmonitor_backend.util import async_download  # check_video
from androidmonitor_backend.version import VERSION

colorama.init()

STARTUP_DATETIME = datetime.utcnow()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    lines.append(
        "\nHandles user registeration and administration of the AndroidMonitor Network"
    )
    lines.append("## Info")
    lines.append(f"  * Version: `{VERSION}`")
    lines.append("  * Started at: `" + STARTUP_DATETIME.isoformat() + " UTC`")
    if IS_TEST:
        lines.append("  * Running in `TEST` mode")
        lines.append("    * x-api-admin-key: *TEST MODE - NO AUTHENTICATION*")
        lines.append("    * DB_URL: " + f"`{DB_URL}`")
        lines.append(f"    * URL: `{URL}`")
        lines.append("    * ALLOW_DB_CLEAR: " + f"`{ALLOW_DB_CLEAR}`")
        lines.append("    * CLIENT_API_KEYS:")
        for client_key in CLIENT_API_KEYS:
            lines.append(f"      * `{client_key}`")
        lines.append("    * Quick Links")
        lines.append(f"      * [Register User]({URL}/v1/add_uid/plaintext)")
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


app.mount(
    "/www",
    StaticFiles(directory=WWW_DIR, html=True, check_dir=True),
    name="www",
)


@app.get("/apk", tags=["client"])
async def apk() -> FileResponse:
    """Get the apk."""
    return FileResponse(
        DOWNLOAD_APK_FILE,
        media_type="application/octet-stream",
        filename="androidmonitor.apk",
    )


@app.get("/apk/update", tags=["client"])
def apk_update() -> JSONResponse:
    """Get the apk."""
    with open(APK_UPDATE_FILE, encoding="utf-8", mode="r") as f:
        json_data: dict = json.loads(f.read())
    json_data["url"] = f"{URL}/apk"
    return JSONResponse(json_data)


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


@app.get("/v1/add_uid", tags=["admin"])
def add_uid(x_api_admin_key: str = ApiKeyHeader) -> JSONResponse:
    """TODO - Add description."""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    ok, uid, created = db_add_uid()
    return JSONResponse({"ok": ok, "uid": uid, "created": created})


@app.get("/v1/add_uid/plaintext", tags=["admin"])
def add_uid_plaintext(x_api_admin_key: str = ApiKeyHeader) -> PlainTextResponse:
    """Returns the uid in plaintext."""
    if not is_authenticated(x_api_admin_key):
        return PlainTextResponse('"error": "Invalid API key"', status_code=401)
    ok, uid, _ = db_add_uid()
    out: str = f"ok: {ok}\nuid: {uid}"
    return PlainTextResponse(out, status_code=200 if ok else 500)


@app.get("/test/download/video", tags=["test"])
def test_download_video() -> FileResponse:
    """Test the download of videos."""
    # file = os.path.join(UPLOAD_DIR, "video.mp4")
    # return FileResponse(file, media_type="video/mp4", filename="video.mp4")
    # get the latest video
    recent_videos: list[VideoItem] = db_get_recent_videos(limit=1)
    if len(recent_videos) == 0:
        return FileResponse("", status_code=404)
    video = recent_videos[0]
    return FileResponse(
        video.uri_video,
        media_type="video/mp4",
        filename="video.mp4",
    )


@app.get("/test/download/videos", tags=["test"])
def test_download_videos(limit: int = 5) -> FileResponse:
    """Test the download of videos."""
    # file = os.path.join(UPLOAD_DIR, "video.mp4")
    # return FileResponse(file, media_type="video/mp4", filename="video.mp4")
    # get the latest video
    recent_videos: list[VideoItem] = db_get_recent_videos(limit=limit)
    if len(recent_videos) == 0:
        return FileResponse("", status_code=404)
    zfile = NamedTemporaryFile(  # pylint: disable=consider-using-with
        suffix=".zip", delete=False
    )
    zfile.close()
    with ZipFile(zfile.name, "w") as zip_obj:
        for i, video in enumerate(recent_videos):
            vidname = f"video{i}.mp4"
            metaname = f"meta{i}.json"
            zip_obj.write(video.uri_video, arcname=vidname)
            zip_obj.write(video.uri_meta, arcname=metaname)
    assert os.path.exists(zfile.name)
    bg_tasks = BackgroundTasks()
    bg_tasks.add_task(lambda: os.remove(zfile.name))
    return FileResponse(
        zfile.name,
        media_type="application/zip",
        filename="videos.zip",
        background=bg_tasks,
    )


@app.get("/test/download/meta", tags=["test"])
def test_download_meta() -> PlainTextResponse:
    """Test the download of meta.json."""
    recent_videos: list[VideoItem] = db_get_recent_videos(limit=1)
    if len(recent_videos) == 0:
        return PlainTextResponse("", status_code=404)
    video = recent_videos[0]
    with open(video.uri_meta, encoding="utf-8", mode="r") as f:
        out = f.read()
    return PlainTextResponse(out, media_type="application/json")


@app.get("/test/download/log", tags=["test"])
def test_download_log() -> PlainTextResponse:
    """Test the download of log.txt."""
    log_ids: list[int] = db_get_recent_logs_ids(limit=1)
    if len(log_ids) == 0:
        return PlainTextResponse("no recent logs", status_code=404)
    log_id = log_ids[0]
    log_text, _ = db_get_log(log_id)
    return PlainTextResponse(log_text)


@app.post("/v1/client_register", tags=["client"])
def register(
    x_uid: str = Header(...), x_client_api_key: str = Header(...)
) -> JSONResponse:
    """Tries to register a device"""
    if not is_authenticated(x_client_api_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    x_uid = x_uid.replace("-", "")
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


def get_path(uid: str) -> str:
    """Returns the path to the upload dir for the given uid."""
    out = os.path.join(UPLOAD_DIR, uid)
    os.makedirs(out, exist_ok=True)
    return out


@app.post("/v1/upload/log", tags=["client"])
async def upload_log(
    log_str: str = Form(),
    x_client_token: str = Header(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    is_client_test = compare_digest(x_client_token, CLIENT_TEST_TOKEN)
    if is_client_test:
        # this is the test client
        log.info("Test client upload called")
        return PlainTextResponse("Test client upload called")
    if not db_is_token_valid(x_client_token):
        return PlainTextResponse("Invalid client registration", status_code=401)
    log.info("Uploading log for %s", x_client_token)
    user = db_get_user_from_token(x_client_token)
    if user is None:
        return PlainTextResponse("Invalid client registration", status_code=401)
    db_add_log(user.uid, log_str)
    return PlainTextResponse("ok")


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
        return PlainTextResponse("Test client upload called")
    if not db_is_token_valid(x_client_token):
        return PlainTextResponse("Invalid client registration", status_code=401)
    if vidfile.filename is None:
        return PlainTextResponse("invalid filename", status_code=400)
    log.info("Upload called with file: %s", vidfile.filename)
    user = db_get_user_from_token(x_client_token)
    if user is None:
        return PlainTextResponse("Invalid client registration", status_code=401)
    upload_dir = get_path(user.uid)
    log.info("Upload dir: %s", upload_dir)
    vidfilename = vidfile.filename
    vidfile_path = os.path.join(upload_dir, vidfilename)
    metafile_path = os.path.splitext(vidfile_path)[0] + ".json"
    try:
        await async_download(metadata, metafile_path)
        await metadata.close()
        log.info("Metafile file: %s", metafile_path)
        await async_download(vidfile, vidfile_path)
        await vidfile.close()
        log.info("Video file: %s", vidfile_path)
        db_register_upload(uid=user.uid, uri_video=vidfile_path, uri_meta=metafile_path)
        return PlainTextResponse(f"Uploaded {vidfile_path} and {metafile_path}")
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("Error during upload: %s", exc)
        if os.path.exists(vidfile_path):
            os.remove(vidfile_path)
        if os.path.exists(metafile_path):
            os.remove(metafile_path)
        return PlainTextResponse(str(exc), status_code=500)


@app.post("/test/upload", tags=["test"])
async def test_upload(
    datafile: UploadFile = File(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    log.info("/test/upload with file: %s", datafile.filename)
    if datafile.filename is None:
        return PlainTextResponse("invalid filename", status_code=400)
    with TemporaryDirectory() as temp_dir:
        temp_datapath: str = os.path.join(temp_dir, datafile.filename)
        await async_download(datafile, temp_datapath)
        log.info("Download test file %s to %s", datafile.filename, temp_datapath)
    return PlainTextResponse(f"Uploaded {datafile.filename} to {temp_datapath}")


@app.get("/v1/list/uids", tags=["admin"])
def log_file(
    x_api_admin_key: str = ApiKeyHeader,
) -> JSONResponse:
    """List all uids"""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    rows = db_get_recent()
    # convert to json
    out = []
    for row in rows:
        item = {"uid": row.uid, "created": row.created.isoformat()}
        out.append(item)
    return JSONResponse(out)


@app.get("/v1/list/uploads/{uid}", tags=["admin"])
def list_uid_uploads(uid: str, x_api_admin_key: str = ApiKeyHeader) -> JSONResponse:
    """Get's all uploads from the user with the given uid."""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    uid = uid.replace("-", "")
    rows = db_get_uploads(uid)
    out = []
    for row in rows:
        item = {
            "id": row.id,
            "uri_video": row.uri_video,
            "uri_meta": row.uri_meta,
            "created": row.created.isoformat(),
        }
        out.append(item)
    return JSONResponse(out)


@app.get("/v1/list/logs/{uid}", tags=["admin"])
def list_uid_logs(uid: str, x_api_admin_key: str = ApiKeyHeader) -> JSONResponse:
    """Lists all the logs gathered from the user with the given uid."""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    uid = uid.replace("-", "")
    rows: list[tuple[int, datetime]] = db_list_logs(uid)
    out = []
    for row in rows:
        id = row[0]
        created = row[1]
        item = {"id": id, "created": created}
        out.append(item)
    return JSONResponse(out)


@app.get("/v1/download/video/{vid_id}", tags=["admin"])
def download_video(vid_id: int, x_api_admin_key: str = ApiKeyHeader) -> FileResponse:
    """Download video file via id"""
    if not is_authenticated(x_api_admin_key):
        return FileResponse("", status_code=401)
    vid_info: VideoItem | None = db_get_video(vid_id)
    if vid_info is None:
        return FileResponse("", status_code=404)
    return FileResponse(vid_info.uri_video, media_type="video/mp4")


@app.get("/v1/download/meta/{vid_id}", tags=["admin"])
def download_meta(vid_id: int, x_api_admin_key: str = ApiKeyHeader) -> JSONResponse:
    """Download meta file via id"""
    if not is_authenticated(x_api_admin_key):
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    vid_info: VideoItem | None = db_get_video(vid_id)
    if vid_info is None:
        return JSONResponse({"error": "Invalid id"}, status_code=404)
    with open(vid_info.uri_meta, encoding="utf-8", mode="r") as meta_file:
        meta_json = json.load(meta_file)
    return JSONResponse(meta_json)


@app.get("/v1/download/log/{log_id}", tags=["admin"])
def download_log(log_id: int, x_api_admin_key: str = ApiKeyHeader) -> PlainTextResponse:
    """Download log file via id"""
    if not is_authenticated(x_api_admin_key):
        return PlainTextResponse("Invalid API key", status_code=401)
    log_str = db_get_log(log_id)
    if log_str is None:
        return PlainTextResponse("Invalid id", status_code=404)
    return PlainTextResponse(log_str)


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
    async def clear(x_api_admin_key: str = ApiKeyHeader) -> PlainTextResponse:
        """TODO - Add description."""
        if not is_authenticated(x_api_admin_key):
            return PlainTextResponse("Invalid API key", status_code=401)
        log.critical("Clear called")
        db_clear()
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
    main()
