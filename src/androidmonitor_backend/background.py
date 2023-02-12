"""
Background tasks
"""

import sys
import time

from androidmonitor_backend.log import make_logger
from androidmonitor_backend.db import db_expire_old_uuids
from androidmonitor_backend.settings import TASK_SLEEP_TIME, EXPIRE_UID_TIME

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
