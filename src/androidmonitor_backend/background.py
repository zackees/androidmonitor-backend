"""
Background tasks
"""

import os
import sys
import time

from androidmonitor_backend.log import make_logger
from androidmonitor_backend.db import db_expire_old_uuids

DEFAULT_TASK_SLEEP_TIME = 60 * 5
DEFAULT_EXPIRE_UID_TIME = 60 * 60  # 1 hour
EXPIRE_UID_TIME = int(os.environ.get("EXPIRE_UID_TIME", DEFAULT_EXPIRE_UID_TIME))
TASK_SLEEP_TIME = int(os.environ.get("TASK_SLEEP_TIME", DEFAULT_TASK_SLEEP_TIME))

log = make_logger(__name__, "background.log")


def run_task() -> None:
    """TODO - Add description."""
    log.info("Running background task")
    db_expire_old_uuids(EXPIRE_UID_TIME)


def main() -> int:
    """TODO - Add description."""
    log.info("Starting background task")
    while True:
        try:
            time.sleep(TASK_SLEEP_TIME)
            run_task()
        except KeyboardInterrupt:
            log.info("Exiting background task")
            return 0


if __name__ == "__main__":
    sys.exit(main())
