"""
Example test.
"""
import unittest
from datetime import datetime

from androidmonitor_backend.util import parse_datetime


class DateTimeTester(unittest.TestCase):
    """Example tester."""

    def test_datetime_parsing(self) -> None:
        """Example tester."""
        sample_str = "2023-04-12T17:50:11.69-08:00"
        dt = parse_datetime(sample_str)  # Will throw exception if not valid
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 4)
        self.assertEqual(dt.day, 12)
        self.assertEqual(dt.hour, 17)
        self.assertEqual(dt.minute, 50)
        self.assertEqual(dt.second, 11)
        self.assertEqual(dt.microsecond, 690000)
        utcoffset_seconds = dt.tzinfo.utcoffset(dt).seconds  # type: ignore
        self.assertEqual(utcoffset_seconds, 57600)
        dt_str = dt.isoformat()
        self.assertEqual(dt_str, "2023-04-12T17:50:11.690000-08:00")


if __name__ == "__main__":
    unittest.main()
