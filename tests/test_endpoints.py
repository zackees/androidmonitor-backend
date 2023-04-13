"""
Tests the endpoints of the API.
"""
import contextlib
import json
import threading
import time
import unittest

import requests  # type: ignore
import uvicorn
from uvicorn.config import Config

from androidmonitor_backend import settings

APP_NAME = "androidmonitor_backend.app:app"
HOST = "localhost"
PORT = 4422  # Arbitrarily chosen.
REMOTE_ENDPOINT = "https://androidmonitor.internetwatchdogs.org/v1/info"
__version__ = "1.0.0"
ADD_UID_ENDPOINT = "https://api.androidmonitor.org/v1/add_uid"
# Credit:
# https://github.com/zackees/vids-db-server/blob/main/vids_db_server/testing/run_server_in_thread.py


# Surprisingly uvicorn does allow graceful shutdowns, making testing hard.
# This class is the stack overflow answer to work around this limitiation.
# Note: Running this in python 3.8 and below will cause the console to spew
# scary warnings during test runs:
#   ValueError: set_wakeup_fd only works in main thread
class ServerWithShutdown(uvicorn.Server):
    """Adds a shutdown method to the uvicorn server."""

    def install_signal_handlers(self):
        pass


class EndpointTester(unittest.TestCase):
    """Test harness for the endpoints of the API."""

    @contextlib.contextmanager
    def run_server_in_thread(self):
        """
        Useful for testing, this function brings up a server.
        It's a context manager so that it can be used in a with statement.
        """
        config = Config(
            APP_NAME, host=HOST, port=PORT, log_level="info", use_colors=False
        )
        server = ServerWithShutdown(config=config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            while not server.started:
                time.sleep(1e-3)
            time.sleep(1)
            yield
        finally:
            server.should_exit = True
            thread.join()


def test_getinfo(self) -> None:
    """Test the getinfo endpoint."""
    with self.run_server_in_thread():
        response = requests.get(f"{REMOTE_ENDPOINT}/v1/info", timeout=5)
        assert response.ok, f"Request failed with status code {response.status_code}"
        assert (
            response.status_code == 200
        ), f"Expected status 200 but got {response.status_code}"
        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError as e:
            response_data = None
            print(f"Failed to decode response as JSON: {e}")
        expected = {"Version": __version__, "API Version": "1.0"}
        assert response_data == expected, f"Expected {expected} but got {response_data}"


def test_add_uid(self) -> None:
    """Test the add_uid endpoint."""
    with self.run_server_in_thread():
        # Set up the request headers
        headers = {
            "accept": "application/json",
            "x-api-admin-key": settings.API_ADMIN_KEY,
        }
        # Make the request to add a UID
        response = requests.get(ADD_UID_ENDPOINT, headers=headers, timeout=5)
        # Check the response was successful
        assert response.ok, f"Request failed with status code {response.status_code}"
        assert (
            response.status_code == 200
        ), f"Request failed with status code {response.status_code}"
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {}
            assert False, "Failed to decode response JSON"
        assert response_data.get(
            "success", False
        ), f"Expected 'success' key to be True but got {response_data.get('success')}"
        uid = response_data.get("uid", None)
        # Query the list of UIDs to check that the UID was added
        response = requests.get(
            "https://api.androidmonitor.org/v1/list/uids", timeout=5
        )
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {}
            assert False, "Failed to decode response JSON"
        assert response_data, "Failed to list UIDs"
        # Check that the UID was added to the list
        uid_list = response_data.get("uids", [])
        assert len(uid_list) == 1, f"Expected 1 UID but found {len(uid_list)} UIDs"
        assert uid_list[0] == uid, f"Expected UID {uid} but found UID {uid_list[0]}"
        # Register the client with the UID
        payload = {
            "uid": uid,
            "client_api_key": list(settings.CLIENT_API_KEYS)[0],
        }
        response = requests.post(
            "https://api.androidmonitor.org/v1/client_register", json=payload, timeout=5
        )
        response_data = response.json()
        # Check that the registration was successful
        assert response_data.get(
            "success", False
        ), "Failed to register client: success=False"


if __name__ == "__main__":
    unittest.main()
