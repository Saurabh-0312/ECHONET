# ops/README — HTTPS deployment for ECHONET

This document describes the automated HTTPS deployment flow and the helper script in this repository.

Files of interest

- `scripts/deploy-https.sh` — Idempotent script to bring up docker compose, request Let's Encrypt certs using the webroot plugin, copy certs into the project mount, reload nginx, and install a renewal cron if needed. Run from the repo root on the server.

- `certbot/` — local project folders used as mounts into the frontend container:
  - `certbot/www` — webroot for ACME challenges (mounted as `/var/www/certbot` in the frontend container)
  - `certbot/conf` — copied certs (if you choose to copy them from `/etc/letsencrypt`) or used when running certbot with custom config-dir.

- `docker-compose.yml` — the frontend service now mounts `/etc/letsencrypt` from the host (read-only) and `./certbot/www` as the ACME webroot. This ensures nginx sees the same certificates that certbot writes on the host.

- `.github/workflows/deploy.yml` — the GitHub Actions deploy workflow now contains a guarded block that attempts a one-time certificate issuance using the `certbot/certbot` docker image if `certbot/conf/live/echonet.live/fullchain.pem` is missing on the server after deploy. The workflow expects a repo secret `CERT_EMAIL` with a contact email.

Notes and recommendations

- For production, prefer mounting the host `/etc/letsencrypt` into the frontend container (this repo does so) and running certbot on the host. This minimizes file copy complexity and ensures certbot and nginx share a single canonical location for certs.

- The repository previously contained a dummy-cert generator (`Frontend/docker-entrypoint.d/10-generate-dummy-cert.sh`) that would create self-signed certs if Let's Encrypt certs were missing. That script has been removed to avoid confusion. If you need a development fallback, consider making dummy generation opt-in behind an environment variable.

- Certbot automatic renewal: If certbot is installed from the OS package, it usually configures a systemd timer. The `scripts/deploy-https.sh` script will install a cron fallback if no systemd timer is present. Test renewal with:

```
sudo certbot renew --dry-run
```

- The GitHub Action's one-time issuance uses the repository secret `CERT_EMAIL` to pass an email address to certbot. Add this secret in the repository settings when enabling the workflow.

Troubleshooting

- If the site serves a self-signed certificate after running certbot, check whether nginx is reading the same certificate files as certbot wrote. Either mount `/etc/letsencrypt` into the container or copy the files into `./certbot/conf` and reload the frontend container.

- Check `/var/log/letsencrypt/letsencrypt.log` for certbot errors.

Support

If you want, I can:

- Remove the copy-based cert approach and update `docker-compose.yml` to rely only on `/etc/letsencrypt` mount (I have applied this), or reverse to using only repo-mounted certs and update `scripts/deploy-https.sh` to request certs directly into `./certbot/conf`.
- Add an ops playbook with exact commands and checks for first-time setup and disaster recovery.

---
Generated automatically by the deployment assistant.