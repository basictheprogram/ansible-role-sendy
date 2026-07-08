# DESIGN.md — ansible-role-sendy

Authoritative spec for this role. If code disagrees with this file, this
file is right — flag the discrepancy and ask before changing this file
to match the code.

## Scope

Upgrades an existing self-hosted Sendy installation on Debian/Ubuntu,
following HelloSendy's official four-rule upgrade procedure
(https://sendy.co/get-updated). Pairs with the sibling
`realtime.sendy_install` role, which handles first-time installs. OS
patching and first-time installation are both explicitly out of scope
for this role.

## Settled decisions

* **OS patching = separate role.** This role does not touch `apt` or `yum`.
* **Uploads dir = never modified.** Rule 3 removes `/uploads/` from the
  staged build; the live `/uploads/` is always left as-is.
* **Staging dir = always wiped** at the start and end of deploy. No
  partial-state leftovers between runs.
* **Sync tool = `ansible.posix.synchronize`** (rsync).
  `ansible.builtin.copy` recursive is slower and doesn't preserve
  permissions cleanly across large directory trees.
* **Backup = timestamped directory, not a tarball.** Easier to inspect
  and restore individual files without extracting an archive.
* **Smoke test = optional HTTP GET** via `ansible.builtin.uri`. Not a
  deep health check — just confirms the web server responds after the
  deploy.
* **`sendy_install_dir` deliberately shares its name with the sibling
  `realtime.sendy_install` role's own variable** (confirmed 2026-07-08
  against a real production host's host_vars, which sets it once and
  both roles pick it up) — this is an intentional shared variable, not a
  naming collision.
* **Version guard** (added 2026-07-08, mirroring `realtime.sendy_install`'s
  pattern) — the role parses a semantic version (X.Y.Z) from
  `sendy_zip_src`'s filename (e.g. `sendy-7.0.6.zip` -> `7.0.6`) and
  records the version it upgrades to at `sendy_version_marker`
  (`/var/lib/sendy_upgrade/version` by default, outside the web root).
  Unlike the install role's same-or-older guard, this role's guard only
  fails on a strictly **older** zip — this role must stay safe to re-run
  (see `CLAUDE.md`'s Idempotency convention and the `idempotence` step in
  `molecule/default/molecule.yml`), so re-applying the same version is
  allowed rather than blocked. `sendy_force_reupgrade` bypasses the guard
  entirely, for testing.

## Open questions

If a task touches one of these, leave a `# TODO(open-q):` comment:

* **Database migrations** — Sendy 7 may require schema changes. The
  current role has no DB migration step; confirm with HelloSendy docs
  before adding one.
* **PHP-FPM pool reload** — if the target runs PHP-FPM separately from
  the web server, the handler may need to reload the FPM pool in
  addition to (or instead of) restarting Apache/nginx. Not needed for
  the production host reviewed 2026-07-08 (confirmed
  `php_enable_php_fpm: false` there), but the role stays generic since
  other consumers may differ.
* **Smoke test default URL may not reach Sendy behind name-based virtual
  hosting** (found 2026-07-08 while reviewing a real production host's
  host_vars) — `sendy_smoke_test_url` defaults to
  `http://{{ ansible_facts.default_ipv4.address }}/`, but a target configured
  with named Apache vhosts (and no default vhost) will not route a
  bare-IP request with no Host header to Sendy. Always override
  `sendy_smoke_test_url` explicitly in host_vars for such targets; this
  role does not detect or warn about the mismatch itself.

## Consumer side notes

<!-- TODO: fill in consumer notes -->
