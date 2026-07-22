# TODO — ansible-role-sendy

Flagged during the 2026-07-03 template sync session. Updated 2026-07-08
after aligning this role with the sibling `realtime.sendy_install` role.
Updated again 2026-07-22 after a full `ansible-sync-role` pass (Steps
1–14) — this is the first sync session to actually walk Steps 3–13
end-to-end for this role rather than skipping them.

* **2026-07-03 sync gap — resolved 2026-07-22.** The original template
  sync's Steps 7 and 9–12 were written for a `support_users`-style role
  and were skipped rather than adapted. This session walked all of
  Steps 3–13 against this role's actual shape (file-preservation
  upgrade, no packages, no templates) and found the role had already
  been brought up to standard by hand in the interim: preflight
  assertions, the version guard, and the full molecule + testinfra
  suite (backup, deploy preservation, new-file deploy, permissions,
  webserver) all already existed and needed no structural changes.
* **`.github/workflows/ci.yml` does not exist.** The README's CI badge
  is still red. Add the workflow when CI is set up for this repo.
* **`DESIGN.md` — resolved 2026-07-08.** Added, matching the pattern
  established by `realtime.sendy_install`. `CLAUDE.md`'s Settled
  decisions and Open questions sections now point to it instead of
  duplicating the content.
* **`meta/argument_specs.yml` — resolved 2026-07-08.** Added, documenting
  the full public interface including the two new version-guard
  variables (`sendy_version_marker`, `sendy_force_reupgrade`).
* **`meta/main.yml`'s `platforms:` key — resolved 2026-07-22.** Removed
  entirely (it was silently ignored by Galaxy and tripped a
  long-standing `ansible-lint` `schema[meta]` false-positive bug — see
  the sync skill's `known-issues.md`). The Debian/Ubuntu version
  support statement now lives in `galaxy_info.description:` instead,
  matching the README's Supported Platforms table exactly.
* **`molecule/default/molecule.yml` verifier block — resolved
  2026-07-22.** Updated to the current sync-skill asset
  (`p: "no:cacheprovider"` in place of `tb: short`). Platform matrix
  itself was already correct and needed no changes.
* **`molecule/requirements.txt` — resolved 2026-07-22.** Re-sorted
  alphabetically to match the sync skill's pinned asset (same version
  floors, just line order).
* **`CLAUDE.md`'s Testing locally / goal-driven-execution sections —
  resolved 2026-07-22.** Neither mentioned `molecule converge` /
  `molecule verify` / `molecule test` despite the role having a full
  molecule suite; both now reference it alongside the existing
  pre-commit and real-inventory dry-run guidance.
* **Decision: preflight task tags kept as `[sendy, sendy_preflight]`,
  not `tags: always`** (2026-07-22). The sync skill defaults to
  `tags: always` for preflight so it can never be bypassed by a
  `--tags` filter, but this role's README documents
  `--tags sendy_deploy` as a supported (caution-flagged) way to skip
  preflight and backup for a quick redeploy. Kept the documented
  escape hatch rather than closing it silently. Revisit if that
  workflow is ever reconsidered.
* **Decision: no OS-family cache-update `pre_tasks` added to
  `molecule/default/converge.yml`** (2026-07-22). The sync skill calls
  for this by default, but this role's own tasks never call `apt`/`dnf`
  — it's pure file/rsync/HTTP work — so the block would be inert for
  this specific role. `prepare.yml` already does its own apt cache
  update before installing the Apache/PHP test fixture, which is the
  only place in this scenario that actually needs it.
* **Heads-up, not acted on: Debian bookworm (12)'s full security
  support window ends ~2026-08** per `scripts/platform-data.json`
  (`last_updated: 2026-05`) — LTS continues to 2028-06, and it's not
  past EOL as of this session (2026-07-22), so it was kept in the
  supported-platform list without asking. Worth a fresh EOL check next
  time this role is synced, since that window closes within weeks of
  this session.
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
