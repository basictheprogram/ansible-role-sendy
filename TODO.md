# TODO — ansible-role-sendy

Flagged during the 2026-07-03 template sync session. Updated 2026-07-08
after aligning this role with the sibling `realtime.sendy_install` role.

* **Preflight and molecule suite were not touched during the 2026-07-03
  template sync.** The sync skill's Steps 7 and 9–12 are written for a
  `support_users`-style role (assert `username`/`shell`/`skel_dir`,
  molecule fixtures with `testuser1` + SSH keys). Sendy has neither
  concept. Since then, `tasks/preflight.yml` gained ansible-core/OS-family
  asserts and a version guard (2026-07-08, mirroring
  `realtime.sendy_install`), and the molecule locale fixture was corrected
  to match a real Sendy release's nested `locale/<lang>/LC_MESSAGES/`
  layout instead of flat PHP files.
* **`.github/workflows/ci.yml` does not exist.** The README's CI badge
  is currently red. Add the workflow when CI is set up for this repo.
* **`DESIGN.md` — resolved 2026-07-08.** Added, matching the pattern
  established by `realtime.sendy_install`. `CLAUDE.md`'s Settled
  decisions and Open questions sections now point to it instead of
  duplicating the content.
* **`meta/argument_specs.yml` — resolved 2026-07-08.** Added, documenting
  the full public interface including the two new version-guard
  variables (`sendy_version_marker`, `sendy_force_reupgrade`).
* **Open questions carried from `DESIGN.md`:**
  * Database migrations — Sendy 7 may require schema changes; no
    migration step exists yet. Confirm with HelloSendy docs before
    adding one.
  * PHP-FPM pool reload — if the target runs PHP-FPM separately from the
    web server, the handler may need to reload the FPM pool in addition
    to (or instead of) restarting Apache/nginx. Confirmed not needed for
    the production host reviewed 2026-07-08 (`php_enable_php_fpm: false`
    there), but the role stays generic.
  * Smoke test default URL vs. name-based virtual hosting — found
    2026-07-08 while reviewing a real production host's host_vars: the
    bare-IP default (`sendy_smoke_test_url`) will not reach Sendy on a
    target with named Apache vhosts and no default vhost. That host's
    own host_vars should set `sendy_smoke_test_url` explicitly before
    the next real upgrade — this is an inventory-repo change, not a role
    change, and hasn't been made yet.
