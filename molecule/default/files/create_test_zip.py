#!/usr/bin/env python3
"""Build a minimal fake Sendy 7 build zip for molecule testing.

The zip mirrors the directory layout that a real Sendy release produces
after extraction: a single top-level ``sendy/`` directory containing all
role and asset files.

Marker strings embedded in each file let testinfra distinguish "new build"
content from "live install" content and assert that the four preservation
rules were applied correctly.

Usage::

    python3 create_test_zip.py <output_zip_path>
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Build manifest
# ---------------------------------------------------------------------------
# Keys are paths inside the zip (top-level dir is ``sendy/``).
# Values are the file contents.
#
# NEW_BUILD_CONFIG and NEW_BUILD_HTACCESS markers must NOT appear in the live
# install after upgrade — testinfra asserts their absence.
# NEW_IN_7 markers appear in files that the role is expected to deploy fresh.
# ---------------------------------------------------------------------------

_BUILD_FILES: dict[str, str] = {
    # includes/ ── config.php must be replaced by the live version
    "sendy/includes/config.php": (
        "<?php\n"
        "// NEW_BUILD_CONFIG — must NOT survive into the live install\n"
        "$dbHost = 'build-placeholder';\n"
    ),
    # New PHP file introduced in Sendy 7 — should land in the live install
    "sendy/includes/functions.php": (
        "<?php\n"
        "// NEW_IN_7 functions.php\n"
    ),
    # locale/ ── stock locale from the new build; custom locale must overlay it
    "sendy/locale/en_US.php": (
        "<?php\n"
        "// NEW_IN_7 en_US.php\n"
        '$lang["confirm"] = "Please confirm.";' + "\n"
    ),
    # uploads/ ── the entire directory must be removed from the build before sync
    "sendy/uploads/.gitkeep": "",
    # .htaccess ── must be removed from the build when preserve_htaccess=true
    "sendy/.htaccess": (
        "# NEW_BUILD_HTACCESS — must NOT survive into the live install\n"
        "Options -Indexes\n"
    ),
    # Core application files — should be deployed into the live install
    "sendy/index.php": (
        "<?php\n"
        "// Sendy 7.0.01 NEW VERSION\n"
        'echo "Sendy 7.0.01";' + "\n"
    ),
    "sendy/login.php": (
        "<?php\n"
        "// NEW_IN_7 login.php\n"
    ),
}


def create_zip(output_path: Path) -> None:
    """Write the fake Sendy build zip to *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in _BUILD_FILES.items():
            zf.writestr(name, content)
    print(f"Created test zip ({output_path.stat().st_size} bytes): {output_path}")


def main() -> None:
    """Entry point — parse CLI args and invoke :func:`create_zip`."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_zip_path>", file=sys.stderr)
        sys.exit(1)
    create_zip(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
