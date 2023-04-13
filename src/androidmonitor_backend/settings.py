"""
Settings
"""

# pylint: disable=line-too-long

import os

HAS_URL = "URL" in os.environ
URL = os.environ.get("URL", "http://localhost:8080")
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# UPLOAD_DIR = os.path.join(PROJECT_ROOT, "upload")
DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
UPLOAD_DIR = os.path.join(DATA_DIR, "upload")
LOG_DIR = os.path.join(DATA_DIR, "logs")
LOG_SYSTEM = os.path.join(LOG_DIR, "system.log")
LOG_SIZE = 512 * 1024
LOG_HISTORY = 20
LOGGING_FMT = (
    "%(levelname)s %(asctime)s %(filename)s:%(lineno)s (%(funcName)s) - %(message)s"
)
LOGGING_USE_GZIP = True
UPLOAD_CHUNK_SIZE = 1024 * 64
DEFAULT_TASK_SLEEP_TIME = 60 * 1
DEFAULT_EXPIRE_UID_TIME = 60 * 60  # 1 hour
EXPIRE_UID_TIME = int(os.environ.get("EXPIRE_UID_TIME", DEFAULT_EXPIRE_UID_TIME))
TASK_SLEEP_TIME = int(os.environ.get("TASK_SLEEP_TIME", DEFAULT_TASK_SLEEP_TIME))
# DB_URL = f"sqlite:///{os.path.relpath(DATA_DIR, '.')}/db.sqlite3"
IS_PRODUCTION = os.getenv("IS_PRODUCTION", "0") == "1"
IS_TEST = not IS_PRODUCTION
# Allow db clear if os.enviorment variable is set or IS_TEST
ALLOW_DB_CLEAR = os.getenv("ALLOW_DB_CLEAR", "0") == "1" or IS_TEST
DEFAULT_PROD_DB_URL = "postgresql://androidmonitor_db_user:R4i7lYhwKsmAIlXku8x1WrTepm1PaDfe@dpg-cfdkeqcgqg45rntp0go0-a.oregon-postgres.render.com/androidmonitor_db"
DEFAULT_TEST_DB_URL = f"sqlite:///{DATA_DIR}/db.sqlite3".replace("\\", "/")
DB_URL = os.getenv("DB_URL", DEFAULT_TEST_DB_URL if IS_TEST else DEFAULT_PROD_DB_URL)
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace(
        "postgres://", "postgresql://", 1
    )  # Fix prefix for sqlalchemy
API_ADMIN_KEY = os.getenv("API_KEY", "test")
assert IS_TEST or (API_ADMIN_KEY != "test"), "API_KEY must be set in production"
CLIENT_API_KEYS = frozenset(
    [
        "1Sv2d4TarkgfUu3yzqXClPTzBVB1hRtQQ1hdcs0yW1HqLY8NLG88HAaUBw3VgRWmN6h1vAfmiReRMcPKKMGgPAyStZCzYEPLLzARMjdYWClcjeaYOV3irge5fnvGQiqx"
    ]
)
CLIENT_TEST_TOKEN = "f2f4b921b3593220488fc099f39295e06f6d2cf67cd886853e423ca2900091a70836b1fa21490f76501d2c0e6a55276d8baa124097538b7a0b95e1df703471ff"
APK_DIR = os.path.join(HERE, "apk")
WWW_DIR = os.path.join(HERE, "www")
# DOWNLOAD_APK_FILE = os.path.join(APK_DIR, "app-normal-release.apk")
APK_META_FILE = os.path.join(APK_DIR, "output-metadata.json")
APK_UPDATE_FILE = os.path.join(APK_DIR, "update-changelog.json")

AWS_ACCESS_KEY = "AKIA4CJG3Q3GL2JLHXBZ"
AWS_SECRET_KEY = "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"
AWS_BUCKET_NAME = "androidmonitor-media-vault"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
