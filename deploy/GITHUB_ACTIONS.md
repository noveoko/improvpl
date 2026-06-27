# GitHub Actions deploy setup

## 1. Generate a deploy key (on your laptop)

```bash
ssh-keygen -t ed25519 -C "github-actions-improvpl" -f improvpl_actions -N ""
```

## 2. Authorize on the server (as root)

```bash
cat improvpl_actions.pub >> /home/improvuser/.ssh/authorized_keys
chown improvuser:improvuser /home/improvuser/.ssh/authorized_keys
chmod 600 /home/improvuser/.ssh/authorized_keys
```

## 3. Add GitHub repository secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `SSH_HOST` | `104.248.47.216` |
| `SSH_USER` | `improvuser` |
| `SSH_PRIVATE_KEY` | Entire contents of `improvpl_actions` (private key) |

## 4. Verify

Push to `staging` (deploys staging) or `main` (deploys production), or run **Actions → CI/CD → Run workflow** with a deploy target.

All pushes and PRs run lint, type check, security scan, Django tests, and Playwright before any deploy.

Check server:

```bash
sudo journalctl -u gunicorn -n 20
```