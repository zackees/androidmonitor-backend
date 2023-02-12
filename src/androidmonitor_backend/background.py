"""
Background tasks
"""

import sys
import time

from androidmonitor_backend.log import make_logger

TASK_SLEEP_TIME = 60 * 5

log = make_logger(__name__, "background.log")


def run_task() -> None:
    """TODO - Add description."""
    log.info("Running background task")


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
