"""Tests for post-deploy web server state.

The role restarts the configured web server as a handler.  These tests
confirm the service is running and enabled so the upgrade actually produced
a live, serving installation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import WEBSERVER_SERVICE

if TYPE_CHECKING:
    from testinfra.host import Host


def test_webserver_is_running(host: Host) -> None:
    """Web server must be running after the deploy handler fires."""
    svc = host.service(WEBSERVER_SERVICE)
    assert svc.is_running


def test_webserver_is_enabled(host: Host) -> None:
    """Web server must be enabled to start on reboot."""
    svc = host.service(WEBSERVER_SERVICE)
    assert svc.is_enabled


def test_webserver_port_80_is_listening(host: Host) -> None:
    """Web server must be listening on port 80 after restart."""
    sock = host.socket("tcp://0.0.0.0:80")
    assert sock.is_listening


def test_webserver_process_is_running(host: Host) -> None:
    """At least one apache2 worker process must be active."""
    result = host.run(f"pgrep -c {WEBSERVER_SERVICE}")
    assert result.rc == 0, f"{WEBSERVER_SERVICE} process not found"
    count = int(result.stdout.strip())
    assert count >= 1
