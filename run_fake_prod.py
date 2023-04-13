"""
Setup development environment
"""

# pylint: disable=wrong-import-position

import os

os.environ.setdefault("DOMAIN_NAME", "localhost")
os.environ.setdefault("IS_PRODUCTION", "1")
os.environ.setdefault("DISABLE_AUTH", "0")
os.environ.setdefault("PASSWORD", "1234")
os.environ.setdefault("ADMIN_KEY", "test-prod")
os.environ.setdefault("USE_S3_PATH", "0")
os.environ.setdefault("ALLOW_DB_CLEAR", "1")
os.environ.setdefault("S3_BUCKET", "androidmonitor")
os.environ.setdefault("USE_DB_SQLITE", "1")

from androidmonitor_backend.app import main

if __name__ == "__main__":
    main()
