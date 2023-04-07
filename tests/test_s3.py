"""
This module contains utility functions to create a temporary file with system information
and a function to upload a file to an S3 bucket. It also includes a unit test to ensure
the S3 upload functionality works correctly.

File will be uploaded to:
https://s3.console.aws.amazon.com/s3/buckets/androidmonitor-media-vault?region=us-east-1&tab=objects
"""

import atexit
import os
import random
import socket
import string
import tempfile
import unittest
from datetime import datetime

from androidmonitor_backend.s3 import s3_download_utf8, s3_list, s3_remove, s3_upload

DISABLE_UPLOAD_REMOVE_TEST = True


def create_temp_file(content: str) -> str:
    """
    Create a temporary file containing the current date, computer name,
    IP address, and hostname.

    Returns:
        str: The path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(content)
    atexit.register(os.unlink, temp_file.name)
    return temp_file.name


class S3Tester(unittest.TestCase):
    """Test the S3 upload functionality."""

    def test_upload_and_list(self) -> None:
        """S3 bucket tester using boto."""
        current_date = datetime.now().isoformat()
        computer_name = socket.gethostname()
        ip_address = socket.gethostbyname(computer_name)
        content = ""
        content += f"Date and Time: {current_date}\n"
        content += f"Computer name: {computer_name}\n"
        content += f"IP address: {ip_address}\n"
        content += f"Hostname: {socket.gethostbyaddr(ip_address)[0]}\n"
        temp_file_path = create_temp_file(content=content)
        self.assertTrue(
            os.path.exists(temp_file_path), f"File {temp_file_path} does not exist"
        )
        s3_prefix = "test/androidmonitor-backend"
        s3_key = f"{s3_prefix}/s3_unit_test.txt"
        exc = s3_upload(temp_file_path, s3_key)
        self.assertIsNone(
            exc, f"Exception was raised while attempting to write to a bucket: {exc}"
        )
        object_keys = s3_list(s3_prefix)
        self.assertIsInstance(object_keys, list)
        self.assertIn(s3_key, object_keys)  # type: ignore

    unittest.skipIf(DISABLE_UPLOAD_REMOVE_TEST, "Skipping remove tests")

    def test_upload_download_remove(self) -> None:
        """Test uploading, downloading, and removing a file from the S3 bucket."""
        content = "Test content"
        temp_file_path = create_temp_file(content=content)
        self.assertTrue(
            os.path.exists(temp_file_path), f"File {temp_file_path} does not exist"
        )

        s3_prefix = "test/androidmonitor-backend"
        random_file_name = "".join(random.choices(string.ascii_lowercase, k=10))
        s3_key = f"{s3_prefix}/{random_file_name}.txt"

        exc = s3_upload(temp_file_path, s3_key)
        self.assertIsNone(
            exc, f"Exception was raised while attempting to write to a bucket: {exc}"
        )
        downloaded_content = s3_download_utf8(s3_key)
        # assert downloaded_content is str
        self.assertIsInstance(downloaded_content, str)
        self.assertEqual(content, downloaded_content)
        exc = s3_remove(s3_key)
        self.assertIsNone(
            exc, f"Exception was raised while attempting to delete from a bucket: {exc}"
        )
        object_keys = s3_list(s3_prefix)
        # self.assertIsInstance(object_keys, list)
        assert object_keys is list
        self.assertNotIn(s3_key, object_keys)  # type: ignore


if __name__ == "__main__":
    unittest.main()
