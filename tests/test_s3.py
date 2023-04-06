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
import warnings
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

warnings.filterwarnings("ignore")

# Replace the following with your AWS access and secret keys
AWS_ACCESS_KEY = "AKIA4CJG3Q3GL2JLHXBZ"
AWS_SECRET_KEY = "N2YtpOGHyv02An9SOIp9K5x/zx3fOcCwNzvpEhg+"
BUCKET_NAME = "androidmonitor-media-vault"


def create_temp_file() -> str:
    """
    Create a temporary file containing the current date, computer name,
    IP address, and hostname.

    Returns:
        str: The path to the temporary file.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    computer_name = socket.gethostname()
    ip_address = socket.gethostbyname(computer_name)

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(f"Date: {current_date}\n")
        temp_file.write(f"Computer name: {computer_name}\n")
        temp_file.write(f"IP address: {ip_address}\n")
        temp_file.write(f"Hostname: {socket.gethostbyaddr(ip_address)[0]}\n")

    atexit.register(os.unlink, temp_file.name)

    return temp_file.name


def upload_to_s3(local_file_path: str, s3_object_key: str) -> Exception | None:
    """
    Upload a file to the specified S3 bucket.

    Args:
        local_file_path (str): The local path to the file to be uploaded.
        s3_object_key (str): The S3 object key (including the path) where
        the file will be uploaded.

    Returns:
        Exception | None: Returns None if the file is successfully uploaded,
        otherwise returns the exception.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        s3.upload_file(local_file_path, BUCKET_NAME, s3_object_key)
        print(f"File uploaded successfully to {BUCKET_NAME}/{s3_object_key}")
        return None
    except FileNotFoundError as fnfe:
        print("The file was not found")
        return fnfe
    except NoCredentialsError as nce:
        print("Credentials not available")
        return nce
    except ClientError as cerr:
        print(f"An error occurred while uploading the file: {cerr}")
        return cerr
    finally:
        s3.close()


class S3Tester(unittest.TestCase):
    """Test the S3 upload functionality."""

    def test_example(self) -> None:
        """S3 bucket tester using boto."""
        temp_file_path = create_temp_file()
        self.assertTrue(
            os.path.exists(temp_file_path), f"File {temp_file_path} does not exist"
        )

        exc = upload_to_s3(
            temp_file_path, "test/androidmonitor-backend/s3_unit_test.txt"
        )
        self.assertIsNone(
            exc, f"Exception was raised while attempting to write to a bucket: {exc}"
        )


if __name__ == "__main__":
    unittest.main()
