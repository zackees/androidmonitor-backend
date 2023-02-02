"""
Db test.
"""

# pylint: disable=wrong-import-position
# flake8: noqa: E402

import os
import unittest
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["DATA_DIR"] = os.path.join(HERE, "data")

from androidmonitor_backend.db import (
    uuid_table,
    engine,
    db_insert_uuid,
    db_get_recent,
    db_init_once,
    DuplicateError,
)


class DbTester(unittest.TestCase):
    """Example tester."""

    def test_db(self) -> None:
        """Example tester."""
        datetime_str = "2020-01-01 00:00:00"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        db_init_once()
        conn = engine.connect()
        # clear the table
        conn.execute(uuid_table.delete())
        conn.commit()
        conn.close()
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
