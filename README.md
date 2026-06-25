# Improv.pl

English-first improv workshops and jams across Poland. Community-driven city polls, frictionless email registration, zero UI clutter.

**Stack:** Django 5.1+ · SQLite (dev) / PostgreSQL (prod) · Tailwind CDN · Whitenoise · Gunicorn · Nginx · Cloudflare

---

## Local development

### Prerequisites

- Python 3.12+
- Git

### Setup

```bash
cd improvpl
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # edit SECRET_KEY if needed
python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages  # optional: Polish translations
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/

Emails print to the console in dev (`EMAIL_BACKEND=console` in `.env`).

### Sample data

In Django admin, create:

1. **Events** — one Workshop (Warsaw) + one Jam (Kraków)
2. **Polls** — e.g. Wrocław workshop, Gdańsk jam

### Test flows

```bash
# Registration, voting, subscribe — use the website UI

# Close polls (expiry + 100-vote threshold)
python manage.py close_polls

# Dry run (no emails sent, but polls still update — use admin for safe testing)
python manage.py close_polls --dry-run
```

### Polish translations

```bash
python manage.py makemessages -l pl
# edit locale/pl/LC_MESSAGES/django.po
python manage.py compilemessages
```

Switch language via EN | PL in the nav bar.

---

## Project structure

```
improvpl/
├── manage.py
├── requirements.txt
├── .env.example
├── deploy/                  # Production configs
├── improvpl/                # Django settings
└── core/                    # Main app
    ├── models.py            # Subscriber, Event, Registration, Poll, Vote
    ├── views.py
    ├── forms.py
    ├── emails.py
    ├── services.py          # Poll lifecycle logic
    ├── management/commands/close_polls.py
    ├── templates/
    └── static/
```

---

## Production

**Live:** https://improv.pl · https://www.improv.pl/admin/

```
Browser ──HTTPS──► Cloudflare (edge SSL) ──HTTP──► Nginx ──► Gunicorn ──► Django ──► PostgreSQL
                         ▲
              Domain registered at SEOHost.pl
              DNS delegated to Cloudflare
```

| Layer | Details |
|-------|---------|
| Server | Digital Ocean droplet, Ubuntu 24.04 |
| App user | `improvuser` → `/home/improvuser/improvpl` |
| Repo | `git@github.com:noveoko/improvpl.git` |
| DNS / SSL | Cloudflare (proxied A records, Universal SSL) |
| Deploy | Push to `main` → GitHub Actions, or `bash deploy/deploy.sh` on server |

### Server `.env` (not in git)

```env
DEBUG=False
SECRET_KEY=<long-random-string>
ALLOWED_HOSTS=improv.pl,www.improv.pl,<DROPLET_IP>
CSRF_TRUSTED_ORIGINS=https://improv.pl,https://www.improv.pl
DATABASE_URL=postgres://improvuser:<password>@localhost:5432/improvpl
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<brevo-login>
EMAIL_HOST_PASSWORD=<brevo-smtp-key>
DEFAULT_FROM_EMAIL=hello@improv.pl
```

### Initial server setup

Ubuntu packages, PostgreSQL, Gunicorn, and Nginx configs live in `deploy/`. On PostgreSQL 15+ (Ubuntu 24.04), also run as `postgres`:

```sql
ALTER DATABASE improvpl OWNER TO improvuser;
\c improvpl
GRANT ALL ON SCHEMA public TO improvuser;
GRANT CREATE ON SCHEMA public TO improvuser;
```

Allow passwordless Gunicorn restarts for deploys:

```bash
echo 'improvuser ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn' | sudo tee /etc/sudoers.d/improvuser-gunicorn
```

### Cloudflare

1. Add `improv.pl` to Cloudflare (Free plan).
2. DNS records (proxied / orange cloud):

| Type | Name | Content |
|------|------|---------|
| A | `@` | `<DROPLET_IP>` |
| A | `www` | `<DROPLET_IP>` |

3. At SEOHost.pl → **Delegacja DNS** → replace SEOHost nameservers with Cloudflare's.
4. **SSL/TLS → Flexible** while the origin serves HTTP only. Do **not** run Certbot behind the orange cloud proxy (causes redirect loops).
5. Optional hardening: Cloudflare Origin Certificate on the droplet + **Full (strict)**.

### CI/CD (GitHub Actions)

Repo secrets (`Settings → Secrets → Actions`):

| Secret | Value |
|--------|-------|
| `SSH_HOST` | Droplet IP |
| `SSH_USER` | `improvuser` |
| `SSH_PRIVATE_KEY` | Private key whose public half is in `~/.ssh/authorized_keys` |

Server needs a GitHub deploy key (`~/.ssh/github_deploy`) with read access to the repo.

Every push to `main` runs `.github/workflows/deploy.yml`. Manual deploy:

```bash
bash ~/improvpl/deploy/deploy.sh
```

### Cron — close polls daily

As `improvuser`, `crontab -e` (see `deploy/crontab.example`):

```
0 9 * * * /home/improvuser/improvpl/venv/bin/python /home/improvuser/improvpl/manage.py close_polls >> /var/log/improvpl_cron.log 2>&1
```

### Useful commands

```bash
# Logs
sudo journalctl -u gunicorn -n 50
sudo tail -f /var/log/nginx/error.log

# Restart after manual changes
sudo systemctl restart gunicorn

# Reset admin password
cd ~/improvpl && source venv/bin/activate
python manage.py changepassword <username>

# Check DNS (should return Cloudflare IPs when proxied)
nslookup improv.pl 1.1.1.1
```

---

## Admin workflows

- **Create events** — `/admin/core/event/`
- **View registrations** — inline on event page or `/admin/core/registration/`
- **Manage polls** — `/admin/core/poll/` (vote count, active/succeeded flags)
- **Subscribers** — `/admin/core/subscriber/`

Weekly: run `close_polls` (automated via cron) or check poll progress manually.

---

## Post-MVP ideas

- Stripe payments for paid workshops
- django-allauth user accounts
- django-modeltranslation for bilingual event content
- Plausible Analytics
- ICS calendar export
- Instructor self-service dashboard

---

## License

Private — Improv.pl © 2026