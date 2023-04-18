"""
Tests the endpoints of the API.
"""
import contextlib
import json
import threading
import time
import unittest
from datetime import datetime

import requests  # type: ignore
import uvicorn
from uvicorn.config import Config

from androidmonitor_backend.settings import API_ADMIN_KEY, CLIENT_API_KEYS

APP_NAME = "androidmonitor_backend.app:app"
HOST = "localhost"
PORT = 4422  # Arbitrarily chosen.

URL = f"http://{HOST}:{PORT}"
ENDPOINT_ADD_UID = f"{URL}/v1/add_uid"
ENDPOINT_GETINFO = f"{URL}/v1/info"
ENDPOINT_CLIENT_REGISTER = f"{URL}/v1/client_register"
ENDPOINT_IS_CLIENT_REGISTERED = f"{URL}/v1/is_client_registered"
ENDPOINT_LIST_UIDS = f"{URL}/v1/list/uids"
ENDPOINT_LOGGED_IN = f"{URL}/v1/logged_in/operator"


# Surprisingly uvicorn does allow graceful shutdowns, making testing hard.
# This class is the stack overflow answer to work around this limitiation.
# Note: Running this in python 3.8 and below will cause the console to spew
# scary warnings during test runs:
#   ValueError: set_wakeup_fd only works in main thread
class ServerWithShutdown(uvicorn.Server):
    """Adds a shutdown method to the uvicorn server."""

    def install_signal_handlers(self):
        pass


@contextlib.contextmanager
def run_server_in_thread():
    """
    Useful for testing, this function brings up a server.
    It's a context manager so that it can be used in a with statement.
    """
    config = Config(APP_NAME, host=HOST, port=PORT, log_level="info", use_colors=False)
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


class EndpointTester(unittest.TestCase):
    """Test harness for the endpoints of the API."""

    def test_is_logged_in(self) -> None:
        """Test the is_logged_in endpoint."""
        with run_server_in_thread():
            headers = {
                "Accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            response = requests.get(ENDPOINT_LOGGED_IN, headers=headers, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))

    def test_getinfo(self) -> None:
        """Test the getinfo endpoint."""
        with run_server_in_thread():
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            response = requests.get(ENDPOINT_GETINFO, headers=headers, timeout=5)
            content = response.text
            self.assertIn("Version:", content)
            self.assertIn("Started at:", content)

    def test_list_uids(self) -> None:
        """Test the list_uids endpoint."""
        with run_server_in_thread():
            headers = {
                "Accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
                "Content-Type": "application/json",
            }
            payload = json.dumps(
                {"start": "2023-03-18T02:47:14.133Z", "end": "2023-04-18T02:47:14.133Z"}
            )
            response = requests.post(
                ENDPOINT_LIST_UIDS, headers=headers, data=payload, timeout=5
            )
            response.raise_for_status()

    def test_uid_registration(self) -> None:
        """Test that we can add a uid and that it is registered."""
        with run_server_in_thread():
            # Set up the request headers
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            # Make the request to add a UID
            response = requests.get(ENDPOINT_ADD_UID, headers=headers, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            uid = response_data.get("uid", "").replace("-", "")
            self.assertTrue(uid, "Expected UID to be returned")
            # Register the UID with the server
            headers = {
                "x-uid": uid,
                "x-client-api-key": list(CLIENT_API_KEYS)[0],
            }
            response = requests.post(
                ENDPOINT_CLIENT_REGISTER, headers=headers, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            self.assertIsNone(response_data.get("error"))
            token = response_data.get("token")
            self.assertTrue(token, "Expected token to be returned")
            headers = {"x-client-token": token}
            response = requests.get(
                ENDPOINT_IS_CLIENT_REGISTERED, headers=headers, timeout=5
            )

    def test_add_uid(self) -> None:
        """Test the add_uid endpoint."""
        with run_server_in_thread():
            # Set up the request headers
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            # Make the request to add a UID
            response = requests.get(ENDPOINT_ADD_UID, headers=headers, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            uid = response_data.get("uid", "")
            self.assertTrue(uid, "Expected UID to be returned")
            headers = {
                "x-uid": uid,
                "x-client-api-key": list(CLIENT_API_KEYS)[0],
            }
            response = requests.post(
                ENDPOINT_CLIENT_REGISTER, headers=headers, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            self.assertIsNone(response_data.get("error"))
            token = response_data.get("token")
            self.assertTrue(token, "Expected token to be returned")
            # Register the UID with the server
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            # Query the list of UIDs to check that the UID was added
            payload = json.dumps({})
            response = requests.post(
                ENDPOINT_LIST_UIDS, headers=headers, data=payload, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data, "Failed to list UIDs")
            # Check that the UID was added to the list
            uids = [uid_data["uid"] for uid_data in response_data]
            uid = uid.replace("-", "")
            self.assertIn(uid, uids, f"UID {uid} not found in list of UIDs")

    @unittest.skip("Work in progress")
    def test_add_uid_time_range(self) -> None:
        """Test the add_uid endpoint."""
        with run_server_in_thread():
            # Set up the request headers
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            # Make the request to add a UID
            response = requests.get(ENDPOINT_ADD_UID, headers=headers, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            uid = response_data.get("uid", "")
            self.assertTrue(uid, "Expected UID to be returned")
            headers = {
                "x-uid": uid,
                "x-client-api-key": list(CLIENT_API_KEYS)[0],
            }
            response = requests.post(
                ENDPOINT_CLIENT_REGISTER, headers=headers, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data.get("ok"))
            self.assertIsNone(response_data.get("error"))
            token = response_data.get("token")
            self.assertTrue(token, "Expected token to be returned")
            # Register the UID with the server
            headers = {
                "accept": "application/json",
                "x-api-admin-key": API_ADMIN_KEY,
            }
            # Query the list of UIDs to check that the UID was added
            payload = json.dumps(
                {"start": "2023-03-18T02:47:14.133Z", "end": datetime.now().isoformat()}
            )
            response = requests.post(
                ENDPOINT_LIST_UIDS, headers=headers, data=payload, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()
            self.assertTrue(response_data, "Failed to list UIDs")
            # Check that the UID was added to the list
            uids = [uid_data["uid"] for uid_data in response_data]
            uid = uid.replace("-", "")
            self.assertIn(uid, uids, f"UID {uid} not found in list of UIDs")


if __name__ == "__main__":
    unittest.main()
