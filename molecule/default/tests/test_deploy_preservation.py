"""Tests for HelloSendy's four file-preservation rules (tasks/deploy.yml).

Each test is named after the rule it validates.  The docstring states the
exact invariant so failures are unambiguous.

Rules (https://sendy.co/get-updated):
  1. config.php  — live version must survive; new build's must not.
  2. locale/     — custom live files must survive; new build files also land.
  3. uploads/    — live directory and its contents must be completely untouched.
  4. .htaccess   — live version must survive when sendy_preserve_htaccess=true.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import (
    INSTALL_DIR,
    LIVE_CONFIG_MARKER,
    LIVE_HTACCESS_MARKER,
    LIVE_LOCALE_MARKER,
    LIVE_UPLOAD_FILENAME,
    LIVE_UPLOAD_MARKER,
    NEW_BUILD_CONFIG_MARKER,
    NEW_BUILD_HTACCESS_MARKER,
    WEB_GROUP,
    WEB_USER,
)

if TYPE_CHECKING:
    from testinfra.host import Host


# ---------------------------------------------------------------------------
# Rule 1 — config.php: live version survives; new-build version does not
# ---------------------------------------------------------------------------


def test_rule1_config_php_exists_after_upgrade(host: Host) -> None:
    """config.php must still exist in includes/ after the upgrade."""
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert f.exists
    assert f.is_file


def test_rule1_config_php_contains_live_marker(host: Host) -> None:
    """config.php content must be the LIVE version, not the new build's.

    The live install has LIVE_MARKER_CONFIG embedded; the new build zip has
    NEW_BUILD_CONFIG.  After upgrade only the live marker must be present.
    """
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert LIVE_CONFIG_MARKER in f.content_string


def test_rule1_config_php_does_not_contain_new_build_marker(host: Host) -> None:
    """The new build's config.php marker must NOT appear in the live install."""
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert NEW_BUILD_CONFIG_MARKER not in f.content_string


# ---------------------------------------------------------------------------
# Rule 2 — locale/: custom live files survive; new-build locale also lands
# ---------------------------------------------------------------------------


def test_rule2_custom_locale_file_exists(host: Host) -> None:
    """Custom locale file written by prepare.yml must still exist."""
    f = host.file(f"{INSTALL_DIR}/locale/custom_en.php")
    assert f.exists
    assert f.is_file


def test_rule2_custom_locale_file_contains_live_marker(host: Host) -> None:
    """Custom locale file content must be the live version, not overwritten."""
    f = host.file(f"{INSTALL_DIR}/locale/custom_en.php")
    assert LIVE_LOCALE_MARKER in f.content_string


def test_rule2_new_build_locale_file_deployed(host: Host) -> None:
    """New locale file from the build (en_US.php) must also land in locale/."""
    f = host.file(f"{INSTALL_DIR}/locale/en_US.php")
    assert f.exists
    assert f.is_file


def test_rule2_new_build_locale_owned_by_web_user(host: Host) -> None:
    """New locale file must be owned by the web user after deploy."""
    f = host.file(f"{INSTALL_DIR}/locale/en_US.php")
    assert f.user == WEB_USER
    assert f.group == WEB_GROUP


# ---------------------------------------------------------------------------
# Rule 3 — uploads/: live directory is completely untouched
# ---------------------------------------------------------------------------


def test_rule3_uploads_directory_exists(host: Host) -> None:
    """uploads/ directory must still exist after the upgrade."""
    d = host.file(f"{INSTALL_DIR}/uploads")
    assert d.exists
    assert d.is_directory


def test_rule3_live_upload_file_preserved(host: Host) -> None:
    """Pre-existing upload file must not be deleted or replaced."""
    f = host.file(f"{INSTALL_DIR}/uploads/{LIVE_UPLOAD_FILENAME}")
    assert f.exists
    assert f.is_file


def test_rule3_live_upload_file_content_intact(host: Host) -> None:
    """Pre-existing upload file content must be byte-for-byte the live version."""
    f = host.file(f"{INSTALL_DIR}/uploads/{LIVE_UPLOAD_FILENAME}")
    assert LIVE_UPLOAD_MARKER in f.content_string


def test_rule3_new_build_gitkeep_not_synced(host: Host) -> None:
    """The new build's uploads/.gitkeep must NOT appear in the live uploads/.

    uploads/ is excluded from the rsync, so no content from the new build's
    uploads/ should land in the live install.
    """
    f = host.file(f"{INSTALL_DIR}/uploads/.gitkeep")
    assert not f.exists


# ---------------------------------------------------------------------------
# Rule 4 — .htaccess: live version survives (sendy_preserve_htaccess=true)
# ---------------------------------------------------------------------------


def test_rule4_htaccess_exists_after_upgrade(host: Host) -> None:
    """.htaccess must still exist after the upgrade."""
    f = host.file(f"{INSTALL_DIR}/.htaccess")
    assert f.exists
    assert f.is_file


def test_rule4_htaccess_contains_live_marker(host: Host) -> None:
    """.htaccess content must be the LIVE version, not the new build's.

    The live install has LIVE_MARKER_HTACCESS; the new build has
    NEW_BUILD_HTACCESS.  With preserve_htaccess=true only the live marker
    must be present.
    """
    f = host.file(f"{INSTALL_DIR}/.htaccess")
    assert LIVE_HTACCESS_MARKER in f.content_string


def test_rule4_htaccess_does_not_contain_new_build_marker(host: Host) -> None:
    """The new build's .htaccess marker must NOT appear in the live install."""
    f = host.file(f"{INSTALL_DIR}/.htaccess")
    assert NEW_BUILD_HTACCESS_MARKER not in f.content_string
