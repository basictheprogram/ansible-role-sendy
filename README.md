# ansible-role-sendy

[![CI](https://github.com/basictheprogram/ansible-role-sendy/actions/workflows/ci.yml/badge.svg)](https://github.com/basictheprogram/ansible-role-sendy/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-sendy-blue.svg?style=popout-square)](https://galaxy.ansible.com/realtime/sendy)
[![Ansible Role](https://img.shields.io/ansible/role/d/realtime/sendy.svg?style=popout-square)](https://galaxy.ansible.com/realtime/sendy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ansible role that automates the [HelloSendy upgrade procedure](https://sendy.co/get-updated)
for a self-hosted Sendy installation on a Linux EC2 instance.

OS patching is out of scope — handled by a separate role and playbook.

---

## What it does

1. **Preflight** — asserts required variables are set, confirms the zip exists
   on the control node, and verifies the live `config.php` is present before
   any changes are made.

2. **Backup** — snapshots `includes/config.php`, `locale/`, and `.htaccess`
   (if present) into a timestamped directory under `sendy_backup_dir`.

3. **Deploy** — uploads and extracts the new build to a staging path, applies
   HelloSendy's four preservation rules, rsyncs the staged build into the live
   install directory, then runs an optional HTTP smoke test.

### HelloSendy's four preservation rules

| # | Rule |
|---|------|
| 1 | Copy `config.php` from live `/includes/` into new build `/includes/` |
| 2 | Copy custom language files from live `/locale/` into new build `/locale/` |
| 3 | Delete `/uploads/` from new build (live uploads dir is never touched) |
| 4 | Delete new build's `.htaccess` when `sendy_preserve_htaccess: true` |

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Ansible ≥ 2.14 | `pip install ansible` |
| `ansible.posix` collection | `ansible-galaxy collection install ansible.posix` |
| Sendy zip on Ansible control node | See source options below |
| SSH key access to target host | Set `ansible_ssh_private_key_file` in host_vars |

### Getting the Sendy zip onto the control node

Download directly from your HelloSendy account, copy from a NAS share, or
use any method that places the zip at the path you set in `sendy_zip_src`.

```bash
# Example: mount a NAS share
sudo mkdir -p /mnt/sendy_releases
sudo mount -t cifs "//nas/releases/sendy" /mnt/sendy_releases \
     -o username=YOUR_USER,password=YOUR_PASS,uid=$(id -u),gid=$(id -g)

# Confirm the zip is present
ls /mnt/sendy_releases/
```

---

## Usage

Set the required host-specific variables in `host_vars/<hostname>.yml`:

```yaml
sendy_zip_src: /mnt/sendy_releases/sendy.zip
sendy_smoke_test_url: https://sendy.example.com/
sendy_webserver_service: apache2
```

Then run:

```bash
# Install required collection
ansible-galaxy collection install ansible.posix

# Dry-run first (no changes made)
ansible-playbook upgrade_sendy.yml --check --diff

# Run for real
ansible-playbook upgrade_sendy.yml
```

### Limit to specific tasks with tags

```bash
# Preflight only
ansible-playbook upgrade_sendy.yml --tags sendy_preflight

# Backup only
ansible-playbook upgrade_sendy.yml --tags sendy_backup

# Deploy only (skips preflight and backup — use with caution)
ansible-playbook upgrade_sendy.yml --tags sendy_deploy
```

---

## Variables

All variables can be overridden in `host_vars`, `group_vars`, or with `-e`.

| Variable | Default | Description |
|---|---|---|
| `sendy_install_dir` | `/var/www/html/sendy` | Live Sendy web root on the remote host |
| `sendy_web_user` | `www-data` | Web server process user |
| `sendy_web_group` | `www-data` | Web server process group |
| `sendy_zip_src` | `""` | **Required.** Path to zip on Ansible control node |
| `sendy_staging_dir` | `/tmp/sendy_upgrade` | Temp dir on remote for extraction |
| `sendy_backup_dir` | `/var/backups/sendy` | Parent dir for timestamped backups |
| `sendy_preserve_htaccess` | `true` | Keep live `.htaccess`, discard new build's |
| `sendy_webserver_service` | `apache2` | Service name restarted after deploy |
| `sendy_run_smoke_test` | `true` | HTTP GET smoke test after deploy |
| `sendy_smoke_test_url` | `http://{{ ansible_default_ipv4.address }}/` | URL to test |
| `sendy_smoke_test_validate_certs` | `true` | Validate TLS in smoke test |

---

## Rollback

A timestamped backup is written to `sendy_backup_dir` (default `/var/backups/sendy`)
before any changes are made. To restore manually:

```bash
BACKUP=/var/backups/sendy/<timestamp>

cp "$BACKUP/config.php"  /var/www/html/sendy/includes/config.php
cp -r "$BACKUP/locale/"  /var/www/html/sendy/locale/
[ -f "$BACKUP/.htaccess" ] && cp "$BACKUP/.htaccess" /var/www/html/sendy/.htaccess

sudo systemctl restart apache2
```

---

## Linting

```bash
# Full lint + format pass before every commit
pre-commit run --all-files
```

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Bob Tanner
