"""
Tests the endpoints of the API.
"""
import contextlib
import threading
import time
import unittest
import json
import requests   # type: ignore
import uvicorn
from uvicorn.config import Config


APP_NAME = "androidmonitor_backend.app:app"
HOST = "localhost"
PORT = 4422  # Arbitrarily chosen.
REMOTE_ENDPOINT = "https://androidmonitor.internetwatchdogs.org/v1/info"
__version__ = '1.0.0'

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
        assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError as e:
            response_data = None
            print(f"Failed to decode response as JSON: {e}")
        expected = {"Version": __version__, "API Version": "1.0"}
        assert response_data == expected, f"Expected {expected} but got {response_data}"


if __name__ == "__main__":
    unittest.main()
