"""
Setup development environment
"""

# pylint: disable=wrong-import-position

import os

os.environ.setdefault("DOMAIN_NAME", "localhost")
os.environ.setdefault("IS_PRODUCTION", "0")
os.environ.setdefault("DISABLE_AUTH", "1")
os.environ.setdefault("PASSWORD", "1234")

from androidmonitor_backend.app import main

if __name__ == "__main__":
    main()
