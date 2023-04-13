"""
Handles upload to the S3 bucket.
"""


import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from androidmonitor_backend.asyncwrap import asyncwrap
from androidmonitor_backend.log import make_logger
from androidmonitor_backend.settings import (
    AWS_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_SECRET_KEY,
)

log = make_logger(__name__)


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


def s3_download(s3_object_key: str, local_file_path: str) -> Exception | None:
    """
    Download a file from the specified S3 bucket.

    Args:
        s3_object_key (str): The S3 object key (including the path) of the file to be read.
        local_file_path (str): The local path to the file to be downloaded.

    Returns:
        Exception | None: Returns the exception if an error occurred, otherwise returns None.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        s3.download_file(AWS_BUCKET_NAME, s3_object_key, local_file_path)
        return None
    except ClientError as cerr:
        log.error("An error occurred while downloading the file: %s", cerr)
        return cerr
    finally:
        s3.close()


def s3_fetch_utf8(s3_object_key: str) -> str | Exception:
    """
    Read a file from the specified S3 bucket.

    Args:
        s3_object_key (str): The S3 object key (including the path) of the file to be read.

    Returns:
        bytes | Exception: Returns the file content as bytes if successful,
        otherwise returns the exception.
    """
    out = s3_fetch(s3_object_key)
    if isinstance(out, Exception):
        return out
    return out.decode("utf-8")


def s3_fetch(s3_object_key: str) -> bytes | Exception:
    """
    Read a file from the specified S3 bucket.

    Args:
        s3_object_key (str): The S3 object key (including the path) of the file to be read.

    Returns:
        bytes | Exception: Returns the file content as bytes if successful,
        otherwise returns the exception.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        response = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_object_key)
        file_content = response["Body"].read()
        return file_content
    except ClientError as cerr:
        log.error("An error occurred while reading the file: %s", cerr)
        return cerr
    finally:
        s3.close()


@asyncwrap
def async_s3_upload(path: str, s3_path: str) -> None:
    """Uploads a file to s3."""
    s3_upload(path, s3_path)


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


# Warning, this function returns an exception because of invalid
# permissions for file removal as of 2023-04-06
def s3_remove(s3_object_key: str) -> Exception | None:
    """
    Delete a file from the specified S3 bucket.

    Args:
        s3_object_key (str): The S3 object key (including the path) of the file to be deleted.

    Returns:
        Exception | None: Returns None if the file is successfully deleted,
        otherwise returns the exception.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        s3.delete_object(Bucket=AWS_BUCKET_NAME, Key=s3_object_key)
        log.info("File deleted successfully from %s/%s", AWS_BUCKET_NAME, s3_object_key)
        return None
    except ClientError as cerr:
        log.error("An error occurred while deleting the file: %s", cerr)
        return cerr
    finally:
        s3.close()
