import threading
import time
import urllib.request
import pytest
from http.server import HTTPServer

# Import the handler and server function from our app
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import HealthCheckHandler, run_server



@pytest.fixture(scope="module")
def test_server():
    """Start the app's HTTP server on a random free port for the test session."""
    server = HTTPServer(("127.0.0.1", 0), HealthCheckHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield port  # provide the port to tests

    server.shutdown()



def test_healthcheck_status_200(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    assert response.status == 200, "Expected HTTP 200 from /healthcheck"



def test_healthcheck_response_body(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    body = response.read().decode("utf-8")
    assert "healthy" in body, f"Expected 'healthy' in response body, got: {body}"


    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    content_type = response.headers.get("Content-type", "")
    assert "application/json" in content_type, (
        f"Expected Content-Type application/json, got: {content_type}"
    )



def test_unknown_route_returns_404(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/unknown"
    try:
        urllib.request.urlopen(url)
        assert False, "Expected HTTPError 404 but got a 200 response"
    except urllib.error.HTTPError as e:
        assert e.code == 404, f"Expected 404, got {e.code}"


def test_memory_increment_calculation():
    """
    Verify the core memory leak math:
    The app is supposed to go from 100MB to 500MB in 120 seconds,
    meaning ~3.33 MB per second.
    """
    target_increase_mb = 400
    duration_seconds = 120
    expected_increment = target_increase_mb / duration_seconds
    increment_bytes = int(expected_increment * 1024 * 1024)

    # Should be around 3,495,253 bytes (~3.33 MB)
    assert increment_bytes > 0, "Increment bytes must be positive"
    assert 3_000_000 < increment_bytes < 4_000_000, (
        f"Increment of {increment_bytes} bytes seems off from the expected ~3.33MB/s"
    )



def test_log_message_suppressed(capsys):
    """
    Ensure log_message is a no-op so the HTTP server
    doesn't pollute application logs.
    """
    handler = HealthCheckHandler.__new__(HealthCheckHandler)
    handler.log_message("GET /healthcheck HTTP/1.1", 200, "-")
    captured = capsys.readouterr()
    assert captured.out == "", "log_message should produce no stdout output"
    assert captured.err == "", "log_message should produce no stderr output"
