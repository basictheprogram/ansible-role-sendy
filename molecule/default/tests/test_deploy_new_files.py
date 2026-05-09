"""Tests that new files from the build were actually deployed.

These complement the preservation tests: we need to verify that while the
role was protecting live content, it also successfully deployed the new
application code from the Sendy 7 build.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import (
    INSTALL_DIR,
    NEW_BUILD_FILES,
    STAGING_DIR,
    WEB_GROUP,
    WEB_USER,
)

if TYPE_CHECKING:
    from testinfra.host import Host


# ---------------------------------------------------------------------------
# New application files from the build
# ---------------------------------------------------------------------------


def test_new_index_php_deployed(host: Host) -> None:
    """index.php must be the new Sendy 7 version after upgrade."""
    f = host.file(f"{INSTALL_DIR}/index.php")
    assert f.exists
    assert f.is_file
    assert "7.0.01" in f.content_string


def test_new_functions_php_deployed(host: Host) -> None:
    """functions.php is a new file in Sendy 7 — must be present after upgrade."""
    f = host.file(f"{INSTALL_DIR}/includes/functions.php")
    assert f.exists
    assert f.is_file


def test_new_login_php_deployed(host: Host) -> None:
    """login.php is a new file in the Sendy 7 build — must be deployed."""
    f = host.file(f"{INSTALL_DIR}/login.php")
    assert f.exists
    assert f.is_file


def test_all_expected_new_build_files_deployed(host: Host) -> None:
    """Every file listed in NEW_BUILD_FILES must exist in the install dir."""
    missing: list[str] = []
    for relative_path in NEW_BUILD_FILES:
        f = host.file(f"{INSTALL_DIR}/{relative_path}")
        if not f.exists:
            missing.append(relative_path)
    assert not missing, f"New build files missing from install dir: {missing}"


def test_new_files_owned_by_web_user(host: Host) -> None:
    """All newly deployed files must be owned by the web user."""
    wrong_owner: list[str] = []
    for relative_path in NEW_BUILD_FILES:
        f = host.file(f"{INSTALL_DIR}/{relative_path}")
        if f.exists and (f.user != WEB_USER or f.group != WEB_GROUP):
            wrong_owner.append(relative_path)
    assert not wrong_owner, (
        f"Files with wrong ownership (expected {WEB_USER}:{WEB_GROUP}): {wrong_owner}"
    )


# ---------------------------------------------------------------------------
# Staging directory cleanup
# ---------------------------------------------------------------------------


def test_staging_directory_removed(host: Host) -> None:
    """Staging directory must be removed after a successful deploy.

    Leaving the staging directory behind would mean a partial-state artifact
    on the server and could mask problems on the next run.
    """
    d = host.file(STAGING_DIR)
    assert not d.exists
