"""Shared fixtures and constants for the sendy_upgrade molecule test suite.

Every testinfra test file imports the constants and fixtures defined here.
The ``host`` fixture is provided automatically by pytest-testinfra; all
other fixtures in this module depend on it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from testinfra.host import Host

# ---------------------------------------------------------------------------
# Path constants — must match defaults/main.yml and converge.yml
# ---------------------------------------------------------------------------

INSTALL_DIR: str = "/var/www/html/sendy"
BACKUP_PARENT_DIR: str = "/var/backups/sendy"
STAGING_DIR: str = "/tmp/sendy_upgrade"
WEB_USER: str = "www-data"
WEB_GROUP: str = "www-data"
WEBSERVER_SERVICE: str = "apache2"

# ---------------------------------------------------------------------------
# Content markers — must match prepare.yml and create_test_zip.py
# ---------------------------------------------------------------------------

# Markers written into the LIVE install by prepare.yml.
# These must survive the upgrade intact.
LIVE_CONFIG_MARKER: str = "LIVE_MARKER_CONFIG"
LIVE_LOCALE_MARKER: str = "LIVE_MARKER_LOCALE"
LIVE_HTACCESS_MARKER: str = "LIVE_MARKER_HTACCESS"
LIVE_UPLOAD_MARKER: str = "LIVE_UPLOAD"

# Markers written into the NEW BUILD zip by create_test_zip.py.
# These must NOT appear in the live install after the upgrade.
NEW_BUILD_CONFIG_MARKER: str = "NEW_BUILD_CONFIG"
NEW_BUILD_HTACCESS_MARKER: str = "NEW_BUILD_HTACCESS"

# File that exists in the live /uploads/ before the upgrade.
LIVE_UPLOAD_FILENAME: str = "live_subscriber_data.csv"

# Files introduced in the new build that should land in the live install.
NEW_BUILD_FILES: list[str] = [
    "includes/functions.php",
    "locale/en_US.php",
    "login.php",
    "index.php",
]

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def backup_dir(host: Host) -> str:
    """Return the path of the single timestamped backup directory.

    The role creates exactly one backup subdirectory per run.  This fixture
    locates it so individual tests can reference files inside it without
    hard-coding the timestamp.
    """
    result = host.run(
        f"find {BACKUP_PARENT_DIR} -mindepth 1 -maxdepth 1 -type d | sort | tail -1"
    )
    assert result.rc == 0, (
        f"Could not list {BACKUP_PARENT_DIR}: {result.stderr}"
    )
    path = result.stdout.strip()
    assert path, (
        f"No timestamped backup directories found under {BACKUP_PARENT_DIR}. "
        "The backup tasks may not have run."
    )
    return path
