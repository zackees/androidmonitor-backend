"""
Settings
"""

# pylint: disable=line-too-long

import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
DATA_UPLOAD_DIR = os.path.join(DATA_DIR, "upload")
LOG_DIR = os.path.join(DATA_DIR, "logs")
LOG_SYSTEM = os.path.join(LOG_DIR, "system.log")
LOG_SIZE = 512 * 1024
LOG_HISTORY = 20
LOGGING_FMT = (
    "%(levelname)s %(asctime)s %(filename)s:%(lineno)s (%(funcName)s) - %(message)s"
)
LOGGING_USE_GZIP = True
UPLOAD_CHUNK_SIZE = 1024 * 64
DEFAULT_TASK_SLEEP_TIME = 60 * 5
DEFAULT_EXPIRE_UID_TIME = 60 * 60  # 1 hour
EXPIRE_UID_TIME = int(os.environ.get("EXPIRE_UID_TIME", DEFAULT_EXPIRE_UID_TIME))
TASK_SLEEP_TIME = int(os.environ.get("TASK_SLEEP_TIME", DEFAULT_TASK_SLEEP_TIME))
# DB_URL = f"sqlite:///{os.path.relpath(DATA_DIR, '.')}/db.sqlite3"
DEFAULT_DB_URL = "postgresql://androidmonitor_db_user:R4i7lYhwKsmAIlXku8x1WrTepm1PaDfe@dpg-cfdkeqcgqg45rntp0go0-a.oregon-postgres.render.com/androidmonitor_db"
DB_URL = os.getenv("DB_URL", DEFAULT_DB_URL)
IS_TEST = os.getenv("IS_TEST", "0") == "1"
API_KEY = os.getenv("API_KEY", "test")


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
