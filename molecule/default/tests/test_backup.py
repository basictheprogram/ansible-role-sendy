"""Tests for tasks/backup.yml.

Verify that the role created a timestamped backup snapshot containing the
live config.php, locale files, and .htaccess — with correct content,
ownership, and permissions — before the upgrade touched anything.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conftest import (
    BACKUP_PARENT_DIR,
    LIVE_CONFIG_MARKER,
    LIVE_HTACCESS_MARKER,
    LIVE_LOCALE_MARKER,
    WEB_GROUP,
    WEB_USER,
)

if TYPE_CHECKING:
    from testinfra.host import Host


# ---------------------------------------------------------------------------
# Backup parent directory
# ---------------------------------------------------------------------------


def test_backup_parent_directory_exists(host: Host) -> None:
    """Backup parent dir must exist (role creates it if absent)."""
    d = host.file(BACKUP_PARENT_DIR)
    assert d.exists
    assert d.is_directory


def test_backup_parent_directory_mode(host: Host) -> None:
    """Backup parent dir must be world-readable but not writable."""
    d = host.file(BACKUP_PARENT_DIR)
    assert d.mode == 0o755


# ---------------------------------------------------------------------------
# Timestamped snapshot directory
# ---------------------------------------------------------------------------


def test_backup_timestamped_directory_created(host: Host, backup_dir: str) -> None:
    """A timestamped subdirectory must have been created under the parent."""
    d = host.file(backup_dir)
    assert d.exists
    assert d.is_directory


def test_backup_directory_mode(host: Host, backup_dir: str) -> None:
    """Backup snapshot dir must be restricted — no world access."""
    d = host.file(backup_dir)
    assert d.mode == 0o750


def test_backup_directory_owner(host: Host, backup_dir: str) -> None:
    """Backup snapshot dir must be owned by the web user."""
    d = host.file(backup_dir)
    assert d.user == WEB_USER
    assert d.group == WEB_GROUP


# ---------------------------------------------------------------------------
# config.php backup
# ---------------------------------------------------------------------------


def test_backup_config_php_exists(host: Host, backup_dir: str) -> None:
    """config.php must be present in the backup snapshot."""
    f = host.file(f"{backup_dir}/config.php")
    assert f.exists
    assert f.is_file


def test_backup_config_php_contains_live_marker(host: Host, backup_dir: str) -> None:
    """Backed-up config.php must contain the live marker, not the new build's."""
    f = host.file(f"{backup_dir}/config.php")
    assert LIVE_CONFIG_MARKER in f.content_string


def test_backup_config_php_mode(host: Host, backup_dir: str) -> None:
    """Backed-up config.php must have the same restricted mode as the live file."""
    f = host.file(f"{backup_dir}/config.php")
    assert f.mode == 0o640


def test_backup_config_php_owner(host: Host, backup_dir: str) -> None:
    """Backed-up config.php must be owned by the web user."""
    f = host.file(f"{backup_dir}/config.php")
    assert f.user == WEB_USER
    assert f.group == WEB_GROUP


# ---------------------------------------------------------------------------
# locale/ backup
# ---------------------------------------------------------------------------


def test_backup_locale_directory_exists(host: Host, backup_dir: str) -> None:
    """locale/ subdirectory must be present in the backup snapshot."""
    d = host.file(f"{backup_dir}/locale")
    assert d.exists
    assert d.is_directory


def test_backup_custom_locale_file_exists(host: Host, backup_dir: str) -> None:
    """The custom locale file written by prepare.yml must be in the backup."""
    f = host.file(f"{backup_dir}/locale/custom_en.php")
    assert f.exists
    assert f.is_file


def test_backup_custom_locale_file_contains_live_marker(
    host: Host, backup_dir: str
) -> None:
    """Backed-up locale file must carry the live marker string."""
    f = host.file(f"{backup_dir}/locale/custom_en.php")
    assert LIVE_LOCALE_MARKER in f.content_string


# ---------------------------------------------------------------------------
# .htaccess backup
# ---------------------------------------------------------------------------


def test_backup_htaccess_exists(host: Host, backup_dir: str) -> None:
    """.htaccess must be present in the backup snapshot."""
    f = host.file(f"{backup_dir}/.htaccess")
    assert f.exists
    assert f.is_file


def test_backup_htaccess_contains_live_marker(host: Host, backup_dir: str) -> None:
    """Backed-up .htaccess must contain the live marker, not the new build's."""
    f = host.file(f"{backup_dir}/.htaccess")
    assert LIVE_HTACCESS_MARKER in f.content_string
