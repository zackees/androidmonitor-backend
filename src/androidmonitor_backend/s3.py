"""
Handles upload to the S3 bucket.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from androidmonitor_backend.log import make_logger
from androidmonitor_backend.settings import (
    AWS_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_SECRET_KEY,
)

log = make_logger(__name__)


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
        log.info("File uploaded successfully to %s/%s", AWS_BUCKET_NAME, s3_object_key)
        return None
    except FileNotFoundError as fnfe:
        # print("The file was not found")
        log.error("The file was not found: %s", fnfe)
        return fnfe
    except NoCredentialsError as nce:
        # print("Credentials not available")
        log.error("Credentials not available: %s", nce)
        return nce
    except ClientError as cerr:
        # print(f"An error occurred while uploading the file: {cerr}")
        log.error("An error occurred while uploading the file: %s", cerr)
        return cerr
    finally:
        s3.close()


def s3_list(s3_prefix: str = "") -> list[str] | Exception:
    """
    List objects in the specified S3 bucket with an optional prefix.

    Args:
        prefix (str, optional): The prefix to filter objects by. Defaults to "".

    Returns:
        list[str] | Exception: Returns a list of object keys if successful,
        otherwise returns the exception.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        result = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=s3_prefix)
        object_keys = [obj["Key"] for obj in result.get("Contents", [])]
        return object_keys
    except ClientError as cerr:
        log.error("An error occurred while listing objects: %s", cerr)
        return cerr
    finally:
        s3.close()
