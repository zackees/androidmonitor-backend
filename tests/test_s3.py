"""
This module contains utility functions to create a temporary file with system information
and a function to upload a file to an S3 bucket. It also includes a unit test to ensure
the S3 upload functionality works correctly.

File will be uploaded to:
https://s3.console.aws.amazon.com/s3/buckets/androidmonitor-media-vault?region=us-east-1&tab=objects
"""

import atexit
import os
import socket
import tempfile
import unittest
from datetime import datetime

from androidmonitor_backend.s3 import s3_upload


def create_temp_file() -> str:
    """
    Create a temporary file containing the current date, computer name,
    IP address, and hostname.

    Returns:
        str: The path to the temporary file.
    """
    current_date = datetime.now().isoformat()
    computer_name = socket.gethostname()
    ip_address = socket.gethostbyname(computer_name)
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(f"Date and Time: {current_date}\n")
        temp_file.write(f"Computer name: {computer_name}\n")
        temp_file.write(f"IP address: {ip_address}\n")
        temp_file.write(f"Hostname: {socket.gethostbyaddr(ip_address)[0]}\n")
    atexit.register(os.unlink, temp_file.name)
    return temp_file.name


class S3Tester(unittest.TestCase):
    """Test the S3 upload functionality."""

    def test_example(self) -> None:
        """S3 bucket tester using boto."""
        temp_file_path = create_temp_file()
        self.assertTrue(
            os.path.exists(temp_file_path), f"File {temp_file_path} does not exist"
        )
        exc = s3_upload(temp_file_path, "test/androidmonitor-backend/s3_unit_test.txt")
        self.assertIsNone(
            exc, f"Exception was raised while attempting to write to a bucket: {exc}"
        )


if __name__ == "__main__":
    unittest.main()
