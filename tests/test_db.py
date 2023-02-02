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

from androidmonitor_backend.db import uuid_table, engine


class DbTester(unittest.TestCase):
    """Example tester."""

    def test_db(self) -> None:
        """Example tester."""
        datetime_str = "2020-01-01 00:00:00"
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        conn = engine.connect()
        # clear the table
        conn.execute(uuid_table.delete())
        ins = uuid_table.insert().values(uuid="test", created=datetime_obj)
        conn.execute(ins)
        select = uuid_table.select().where()
        result = conn.execute(select)
        num_rows = result.cursor.arraysize
        self.assertEqual(num_rows, 1)
        row = result.fetchone()
        self.assertEqual(row.uuid, "test")  # type: ignore
        self.assertEqual(row.created, datetime_obj)  # type: ignore


if __name__ == "__main__":
    unittest.main()
