"""Tests for file permissions and ownership across the install.

Incorrect permissions on config.php or the uploads directory are a
common source of security problems or broken functionality.  These tests
confirm the role sets and preserves the correct modes after every upgrade.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import (
    BACKUP_PARENT_DIR,
    INSTALL_DIR,
    WEB_GROUP,
    WEB_USER,
)

if TYPE_CHECKING:
    from testinfra.host import Host


# ---------------------------------------------------------------------------
# config.php — must be restricted: web user read/write, no world access
# ---------------------------------------------------------------------------


def test_config_php_mode_is_0640(host: Host) -> None:
    """config.php must be mode 0640 — readable by owner/group only."""
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert f.mode == 0o640


def test_config_php_owner_is_web_user(host: Host) -> None:
    """config.php must be owned by the web user."""
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert f.user == WEB_USER


def test_config_php_group_is_web_group(host: Host) -> None:
    """config.php must be in the web group."""
    f = host.file(f"{INSTALL_DIR}/includes/config.php")
    assert f.group == WEB_GROUP


# ---------------------------------------------------------------------------
# uploads/ directory — must be writable by web user, no world write
# ---------------------------------------------------------------------------


def test_uploads_dir_mode_is_0755(host: Host) -> None:
    """uploads/ directory must be mode 0755."""
    d = host.file(f"{INSTALL_DIR}/uploads")
    assert d.mode == 0o755


def test_uploads_dir_owner_is_web_user(host: Host) -> None:
    """uploads/ directory must be owned by the web user."""
    d = host.file(f"{INSTALL_DIR}/uploads")
    assert d.user == WEB_USER


def test_uploads_dir_group_is_web_group(host: Host) -> None:
    """uploads/ directory must be in the web group."""
    d = host.file(f"{INSTALL_DIR}/uploads")
    assert d.group == WEB_GROUP


# ---------------------------------------------------------------------------
# Backup snapshot directory — restricted so only the system can read it
# ---------------------------------------------------------------------------


def test_backup_snapshot_dir_mode_is_0750(host: Host, backup_dir: str) -> None:
    """Backup snapshot dir must be mode 0750 — no world access."""
    d = host.file(backup_dir)
    assert d.mode == 0o750


def test_backup_snapshot_dir_owner_is_web_user(host: Host, backup_dir: str) -> None:
    """Backup snapshot dir must be owned by the web user."""
    d = host.file(backup_dir)
    assert d.user == WEB_USER


def test_backup_snapshot_dir_group_is_web_group(host: Host, backup_dir: str) -> None:
    """Backup snapshot dir must be in the web group."""
    d = host.file(backup_dir)
    assert d.group == WEB_GROUP


def test_backup_config_php_mode_is_0640(host: Host, backup_dir: str) -> None:
    """Backed-up config.php must carry the same restricted mode as the live file."""
    f = host.file(f"{backup_dir}/config.php")
    assert f.mode == 0o640


# ---------------------------------------------------------------------------
# Install directory — sanity check on top-level ownership
# ---------------------------------------------------------------------------


def test_install_dir_owner_is_web_user(host: Host) -> None:
    """Sendy install directory must be owned by the web user."""
    d = host.file(INSTALL_DIR)
    assert d.user == WEB_USER


def test_install_dir_group_is_web_group(host: Host) -> None:
    """Sendy install directory must be in the web group."""
    d = host.file(INSTALL_DIR)
    assert d.group == WEB_GROUP
