"""
Tests that asyncwrap works as expected.
"""


import os
import unittest

from androidmonitor_backend.asyncwrap import asyncwrap

HERE = os.path.dirname(os.path.abspath(__file__))
TESTFILE = os.path.join(HERE, "testfile.txt")


def write_utf8(path: str, content: str) -> None:
    """Writes a string to a file."""
    with open(path, encoding="utf-8", mode="w") as file:
        file.write(content)


def read_utf8(path: str) -> str:
    """Reads a file as UTF-8."""
    with open(path, encoding="utf-8", mode="r") as file:
        return file.read()


@asyncwrap
def async_write_utf8(path: str, content: str) -> None:
    """Async wrapper for write_utf8."""
    write_utf8(path, content)


class AsyncWrapTest(unittest.IsolatedAsyncioTestCase):
    """Tests the async wrapper."""

    async def test_write_to_file(self):
        """Test the async wrapper for write_utf8."""
        content = "success!"

        # Call the async wrapped function
        await async_write_utf8(TESTFILE, content)

        # Check if the content was written to the file
        file_content = read_utf8(TESTFILE)
        self.assertEqual(file_content, content)

        # Clean up the test file
        os.remove(TESTFILE)


if __name__ == "__main__":
    unittest.main()
