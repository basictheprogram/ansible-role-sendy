# Claude Code project notes — ansible-role-sendy

This is an Ansible role that automates upgrading a self-hosted
[Sendy](https://sendy.co) installation on a Linux EC2 instance.
It implements HelloSendy's official four-rule upgrade procedure
(https://sendy.co/get-updated): back up config/locale/.htaccess,
stage the new build, apply preservation rules, rsync into production.

OS patching is out of scope — handled by a separate role and playbook.

---

## Behavioral guidelines

These four rules govern how to work in this repo. They bias toward
caution over speed — for trivial one-liner changes, use judgment.

### 1. Think before writing tasks

**Don't assume. Surface tradeoffs. Ask when uncertain.**

Before adding or changing anything:

* State assumptions explicitly. If a variable could live in `defaults/`,
  `vars/`, or `host_vars`, say which and why before choosing.
* If multiple approaches exist (e.g. `ansible.builtin.copy` vs
  `ansible.posix.synchronize`), present the tradeoff — don't pick silently.
* If the request is ambiguous (which task file? which variable?),
  name the ambiguity and ask. Don't guess and implement.
* If a simpler approach solves the problem, say so and push back.
* If something conflicts with `DESIGN.md`, flag it before proceeding.

### 2. Simplicity first

**Minimum tasks, variables, and template logic that solve the problem.**

* No new default variables beyond what the task being added requires.
* No `when:` conditions for scenarios that have no test coverage.
* No "future-proofing" of the public interface that wasn't asked for.
* If a task block does three things and could do one, split it.

Ask: would a senior Ansible engineer call this overcomplicated? If yes,
simplify.

### 3. Surgical changes

**Touch only what the request requires. Clean up only your own mess.**

When editing existing tasks or defaults:

* Don't reformat adjacent YAML, fix unrelated comments, or clean up
  code that wasn't broken by your change.
* Match the existing style — indentation, quoting, bullet character —
  even if you'd do it differently from scratch.
* If you notice unrelated dead code or stale variables, mention it;
  don't delete it without being asked.

When your change creates orphans:

* Remove `vars`, `when` conditions, or task blocks that YOUR change
  made unreachable.
* Don't remove pre-existing orphans unless explicitly asked.

Every changed line should trace directly to the request.

### 4. Goal-driven execution

**Define the success criteria before starting. Verify before declaring done.**

Transform requests into verifiable outcomes:

* "Add a preflight assertion" → task runs, `molecule verify` passes,
  `pre-commit run --all-files` is clean, YAML parses without error.
* "Fix an idempotency bug" → second `molecule converge` (or playbook run)
  reports zero changed tasks.
* "Refactor a task file" → behavior is identical, `molecule verify`
  passes, lint is clean.

For multi-step changes, state a brief plan before starting:

    1. Edit task        → verify: YAML valid, variable covered in defaults
    2. Update defaults  → verify: new var has a sensible default
    3. Lint             → verify: pre-commit run --all-files clean

Strong success criteria allow independent verification. Weak criteria
("make it work") require constant clarification.

---

## Role-specific notes

### Source of truth

`DESIGN.md` is the authoritative spec. Read it before any non-trivial
change. If code disagrees with `DESIGN.md`, `DESIGN.md` is right —
flag the discrepancy and ask before fixing the design to match the code.

### Design notes

See `DESIGN.md` — scope, settled decisions (four preservation rules,
backup format, sync tool, `sendy_install_dir` shared by name with the
sibling install role, version guard), and open questions (DB migrations,
PHP-FPM reload, smoke test URL vs. name-based vhosts).

### Secrets

Role-specific secret handling: no default variable in this role is
named `*_key`/`*_token`/`*_password`/`*_secret` — the sensitive surface
is a file, not a variable. `config.php` is backed up to the remote host
only — it is never fetched to the control node or logged. Use
`no_log: true` on any task that could expose its content. Production
host credentials (SES SMTP, RDS, Sendy license, etc.) for a real
deployment target are managed via `ansible-vault` in the inventory repo
(e.g. `production/host_vars/<host>/vault.yml` in `ansible-playbooks`) —
this role never manages, references, or ships those values itself.

### Commit scopes

Role-specific subsystem scopes: `preflight`, `backup`, `deploy`,
`config`, `locale`, `uploads`, `htaccess`, `smoke-test`.

### Settled decisions

See `DESIGN.md`'s Settled decisions section — OS-patching exclusion,
uploads-never-modified, staging-always-wiped, `ansible.posix.synchronize`
as the sync tool, timestamped-directory backups, the optional smoke
test, `sendy_install_dir`'s shared naming with the sibling install role,
and the version guard.

### Open questions

See `DESIGN.md`'s Open questions section — database migrations, PHP-FPM
pool reload, and the smoke test URL vs. name-based virtual hosting.

### Implementation order

Work one section at a time. Each item = one focused session and one
commit. Stop and verify between items.

1. `meta/main.yml` — ✅ done
2. `defaults/main.yml` — ✅ done (full public interface)
3. `vars/main.yml` — ✅ done (empty; version tracking moved to
   `defaults/main.yml` + `tasks/preflight.yml` — see `DESIGN.md`)
4. `handlers/main.yml` — ✅ done (Restart webserver)
5. `tasks/preflight.yml` — ✅ done
6. `tasks/backup.yml` — ✅ done
7. `tasks/deploy.yml` — ✅ done (all four preservation rules + smoke test)
8. `molecule/default/` — ✅ done (converge/prepare scaffolded, testinfra
   suite covering backup, deploy, preservation, permissions, and webserver)
9. `templates/` — ⬜ empty; add Jinja2 templates if future tasks require them
10. `files/` — ⬜ empty; add static files if future tasks require them
11. `.github/workflows/ci.yml` — ⬜ does not exist yet; README already links
    a CI badge for it, so the badge is currently red. Add when CI is set up.

### Consumer side notes

<!-- TODO: fill in consumer notes -->

---

## Conventions

* **Commits**: follow the commit message guide in this file exactly.
  Conventional Commits, imperative mood, bodies wrapped at 72 chars,
  asterisk bullets.
* **Lint**: `.ansible-lint`, `.yamllint`, `.pre-commit-config.yaml`
  define the rules. Run `pre-commit run --all-files` before declaring
  work done.
* **Secrets**: never write a credential into a tracked file. `config.php`
  is backed up to the remote host only — it is never fetched to the
  control node or logged. Use `no_log: true` on any task that could
  expose its content. Production host credentials (SES SMTP, RDS, Sendy
  license, etc.) for a real deployment target are managed via
  `ansible-vault` in the inventory repo (e.g. `production/host_vars/<host>/vault.yml`
  in `ansible-playbooks`) — this role never manages, references, or ships
  those values itself.
* **Modules**: prefer FQCNs (`ansible.builtin.copy`, `ansible.posix.synchronize`,
  `ansible.builtin.uri`). The `.ansible-lint` config requires `fqcn-builtins`.
* **Idempotency**: every task should be safe to re-run. The staging dir
  is always wiped before use; the backup dir uses a timestamp so re-runs
  create a new snapshot rather than clobber the previous one.
* **Octal permissions**: always quote them as strings (`"0640"`, `"0755"`)
  — `.yamllint` forbids both implicit and explicit octal literals.
* **Variable prefix**: all public variables are prefixed `sendy_`.
  Internal facts set by `set_fact` are prefixed `_sendy_`.

## Testing locally

* `pre-commit run --all-files` — fast lint/format pass. Run before every commit.
* `molecule converge` then `molecule verify` — fast iteration during
  task work; skips the destroy/create cycle.
* `molecule test` — full role exercise across the OS matrix
  (Debian bookworm/trixie, Ubuntu jammy/noble/resolute). Slow; run
  before declaring a change done.
* `ansible-playbook upgrade_sendy.yml --check --diff` — dry-run against
  real inventory before applying changes.

## When in doubt

Read `DESIGN.md`, then ask. The schemas and decisions there are
load-bearing.

---

## Commit message guide

You are an expert DevOps engineer and professional git commit message
writer. When generating a commit message, follow these steps exactly.

### Step 1 — Retrieve changes

Run:

    git diff --cached

Analyze the full staged diff. This is the **single source of truth**
for what will be committed.

### Step 2 — Understand the change

Determine:

* The **primary purpose** of the change
* The **type of change** (feature, bug fix, refactor, etc.)
* The **most relevant scope** within the role
* Whether the change introduces a **breaking change** for role consumers
* Whether multiple changes should be summarized together

Pay special attention to:

* Changes to `defaults/main.yml` — these define the role's public interface
* Changes to handler names, task names, and tags — consumers may pin to them
* Changes to the four upgrade preservation rules — these are load-bearing
* Changes to `meta/main.yml` — galaxy metadata, min Ansible version, platforms

If multiple files are modified, identify the **dominant intent** rather
than listing every file.

### Step 3 — Select commit type

Use Conventional Commits:

* `feat` — new task, handler, variable, or capability
* `fix` — bug fix or idempotency correction
* `docs` — README, role metadata, inline comments
* `style` — YAML formatting, whitespace, ansible-lint cleanup
* `refactor` — restructure tasks without behavior change
* `perf` — performance improvement (e.g., fewer tasks, faster sync)
* `test` — molecule scenarios, lint config, CI tests
* `chore` — galaxy metadata, dependencies, tooling
* `ci` — GitHub Actions, GitLab CI, pre-commit hooks

### Step 4 — Determine scope

Infer a scope from the role layout or Sendy subsystem.

Common Ansible role scopes: `tasks`, `handlers`, `defaults`, `vars`,
`meta`, `molecule`.

Role-specific subsystem scopes: `preflight`, `backup`, `deploy`,
`config`, `locale`, `uploads`, `htaccess`, `smoke-test`.

Only include a scope when it adds clarity. Prefer the Sendy subsystem
scope for feature-driven changes (e.g., `feat(backup): ...`) and the
role-layout scope for structural changes (e.g., `refactor(tasks): ...`).

### Step 5 — Write the commit message

Format exactly as:

    <type>[optional scope]: <short summary (<=50 chars)>

    <body wrapped at 72 characters>

    [optional footer(s)]

**Subject line rules:**

* Use **imperative mood** ("Add", "Fix", "Update", "Remove")
* Maximum **50 characters**
* Describe the **result**, not the implementation
* Prefer Sendy or Ansible terminology over generic phrasing
  (e.g., "Add locale file backup step", not "Add new task")

**Body rules** (required):

Explain **why the change was made**, focusing on:

* What upgrade scenario or HelloSendy behavior motivated it
* What downstream role consumers need to know to upgrade safely
* Any Ansible version constraints involved

When helpful, summarize key changes using bullet points.

**Bullet rules:**

* Use `*` (asterisk) for all bullets — never `-` or `•`
* Nested bullets indented with two spaces
* No Markdown formatting of any kind

Example:

    * Add locale file discovery step before staging extraction
    * Wire discovered files into deploy overlay loop

**Ansible-specific expectations:**

* Call out new, renamed, or removed default variables
* Note when handler names, tag names, or public task names change
* Mention idempotency improvements when relevant
* Flag changes to `meta/main.yml` (galaxy metadata, minimum Ansible
  version, supported platforms)

### Breaking changes

A change is breaking when it:

* Renames or removes a default variable
* Renames or removes a handler, tag, or public task name
* Changes a default value in a way that alters runtime behavior
* Drops support for an Ansible version or OS platform
* Changes which files are preserved or overwritten during the upgrade

If the diff introduces a breaking change:

* Add `!` after the type/scope in the subject
* Include a footer: `BREAKING CHANGE: <description>`

Examples:

    feat(backup): add locale directory snapshot
    fix(deploy): correct relpath for nested locale files
    refactor(tasks): split deploy into stage and sync steps
    chore(meta): bump minimum Ansible version to 2.15
    docs(readme): add rollback instructions

    feat(defaults)!: rename sendy_webserver variable

    BREAKING CHANGE: sendy_webserver is now sendy_webserver_service;
    update host_vars before upgrading.

### Step 6 — Output rules

Return **only the commit message** — no explanation, no analysis,
no diff, no markdown formatting, no code fences. The output will be
pasted directly into a git commit editor.
