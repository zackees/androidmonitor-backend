"""
Handles upload to the S3 bucket.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from androidmonitor_backend.settings import (
    AWS_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_SECRET_KEY,
)


def s3_upload(local_file_path: str, s3_object_key: str) -> Exception | None:
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
        s3.upload_file(local_file_path, AWS_BUCKET_NAME, s3_object_key)
        # print(f"File uploaded successfully to {AWS_BUCKET_NAME}/{s3_object_key}")
        return None
    except FileNotFoundError as fnfe:
        # print("The file was not found")
        return fnfe
    except NoCredentialsError as nce:
        # print("Credentials not available")
        return nce
    except ClientError as cerr:
        # print(f"An error occurred while uploading the file: {cerr}")
        return cerr
    finally:
        s3.close()
