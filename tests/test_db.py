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
    db_insert_uid,
    db_try_register,
    db_expire_old_uids,
    db_get_uid,
    db_is_client_registered,
)


class DbTester(unittest.TestCase):
    """Example tester."""

    # setup once for class
    @classmethod
    def setUpClass(cls) -> None:
        """Clears the database."""
        db_clear(True)

    def test_insert_uid(self) -> None:
        """Example tester."""
        datetime_str = "2020-01-01 00:00:00"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        db_clear()
        db_insert_uid("test", datetime_obj)
        rows = db_get_recent()
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.uid, "test")  # type: ignore
        self.assertEqual(row.created, datetime_obj)  # type: ignore
        with self.assertRaises(DuplicateError):  # Duplicate uid
            db_insert_uid("test", datetime_obj)

    def test_register(self) -> None:
        """Tests that a uid can be registered"""
        db_insert_uid("test2", datetime.utcnow())
        ok, token = db_try_register("test2")
        self.assertTrue(ok)
        # assert token is 128 chars
        self.assertEqual(len(token), 128)
        # test that client is registered
        self.assertTrue(db_is_client_registered(token, "test2"))
        # assert that the token can't be registered again
        ok, _ = db_try_register("test2")
        self.assertFalse(ok)

    def test_expire(self) -> None:
        """Tests that a uid can be expired"""
        db_insert_uid("test3", datetime.utcnow())
        db_expire_old_uids(max_time_seconds=-99999)
        val = db_get_uid("test3")
        self.assertIsNone(val)


if __name__ == "__main__":
    unittest.main()
