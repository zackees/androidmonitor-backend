"""
Db test.
"""

# pylint: disable=wrong-import-position
# flake8: noqa: E402

import os
import shutil
import unittest
from datetime import datetime

HERE = os.path.relpath(os.path.dirname(__file__), ".")
DB_DIR = os.path.join(HERE, "db_data")
shutil.rmtree(DB_DIR, ignore_errors=True)
os.makedirs(DB_DIR, exist_ok=True)
os.environ["DB_URL"] = f"sqlite:///{DB_DIR}/db.sqlite3"

from androidmonitor_backend.db import (
    DuplicateError,
    db_clear,
    db_get_recent,
    db_insert_uuid,
)


class DbTester(unittest.TestCase):
    """Example tester."""

    def test_insert_uid(self) -> None:
        """Example tester."""
        datetime_str = "2020-01-01 00:00:00"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        db_clear()
        db_insert_uuid("test", datetime_obj)
        rows = db_get_recent()
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.uuid, "test")  # type: ignore
        self.assertEqual(row.created, datetime_obj)  # type: ignore
        with self.assertRaises(DuplicateError):  # Duplicate uuid
            db_insert_uuid("test", datetime_obj)


if __name__ == "__main__":
    unittest.main()
