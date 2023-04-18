"""
Db test.
"""

# pylint: disable=wrong-import-position
# flake8: noqa: E402

import os
import shutil
import unittest
from datetime import datetime, timedelta

HERE = os.path.relpath(os.path.dirname(__file__), ".")
DB_DIR = os.path.join(HERE, "db_data")
shutil.rmtree(DB_DIR, ignore_errors=True)
os.makedirs(DB_DIR, exist_ok=True)
os.environ["DB_URL"] = f"sqlite:///{DB_DIR}/db.sqlite3"

from androidmonitor_backend.db import (
    DuplicateError,
    db_add_log,
    db_clear,
    db_expire_old_uids,
    db_get_log,
    db_get_recent,
    db_get_uploads,
    db_get_user_from_token,
    db_insert_uid,
    db_is_client_registered,
    db_list_logs,
    db_register_upload,
    db_to_string,
    db_try_register,
)


class DbTester(unittest.TestCase):
    """Example tester."""

    # setup once for class
    @classmethod
    def setUpClass(cls) -> None:
        """Clears the database."""
        db_clear()

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
        val = db_get_user_from_token("test3")
        self.assertIsNone(val)

    def test_register_upload(self) -> None:
        """Tests that a uid can be expired"""
        db_clear()
        db_insert_uid("0000", datetime.utcnow())
        start: datetime = datetime.utcnow()
        end = start + timedelta(seconds=1)
        db_register_upload(
            uid="0000",
            uri_video="/tmp/vid.mp4",
            appname="com.google",
            start=start,
            end=end,
            uri_meta="/tmp/meta.json",
        )
        db_str = db_to_string()
        vids = db_get_uploads("0000")
        self.assertEqual(len(vids), 1, f"Expected 1 video, got {len(vids)}, {db_str}")
        vid = vids[0]
        self.assertEqual(vid.user_uid, "0000")
        self.assertEqual(vid.uri_video, "/tmp/vid.mp4")
        self.assertEqual(vid.uri_meta, "/tmp/meta.json")

    def test_db_logs(self) -> None:
        """Tests that a log can be added, listed and retrieved."""
        db_clear()
        db_insert_uid("0000", datetime.utcnow())
        db_add_log("0000", "test")
        log_list: list[tuple[int, datetime]] = db_list_logs("0000")
        self.assertEqual(len(log_list), 1)
        log_id = log_list[0][0]
        self.assertEqual(1, log_id)
        log_str, _ = db_get_log(log_id)
        self.assertEqual("test", log_str)


if __name__ == "__main__":
    unittest.main()
