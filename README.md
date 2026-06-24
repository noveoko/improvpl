# Improv.pl

English-first improv workshops and jams across Poland. Community-driven city polls, frictionless email registration, zero UI clutter.

**Stack:** Django 5.1+ · SQLite (dev) / PostgreSQL (prod) · Tailwind CDN · Whitenoise · Gunicorn · Nginx

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

## Deployment (Digital Ocean)

Target: Ubuntu 24.04 droplet, ~$6/mo (1 GB RAM, 1 vCPU).

### 1. System prep

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv python3-dev libpq-dev \
  postgresql postgresql-contrib nginx certbot python3-certbot-nginx -y
```

### 2. App user & code

```bash
sudo useradd -m -s /bin/bash improvuser
sudo passwd improvuser
sudo usermod -aG www-data improvuser

su - improvuser
git clone YOUR_GITHUB_REPO ~/improvpl
cd ~/improvpl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE improvpl;
CREATE USER improvuser WITH PASSWORD 'your-strong-password';
GRANT ALL PRIVILEGES ON DATABASE improvpl TO improvuser;
\q
```

### 4. Environment

```bash
nano ~/improvpl/.env
```

```env
DEBUG=False
SECRET_KEY=generate-a-long-random-string-here
ALLOWED_HOSTS=improv.pl,www.improv.pl,YOUR_DROPLET_IP
DATABASE_URL=postgres://improvuser:your-strong-password@localhost:5432/improvpl
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-brevo-login
EMAIL_HOST_PASSWORD=your-smtp-password
DEFAULT_FROM_EMAIL=hello@improv.pl
```

### 5. Migrate & static

```bash
cd ~/improvpl && source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py compilemessages
```

### 6. Gunicorn (systemd)

```bash
sudo cp ~/improvpl/deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

Ensure the socket is readable by Nginx:

```bash
sudo chmod 755 /home/improvuser
sudo chown improvuser:www-data /home/improvuser/improvpl/improvpl.sock
```

### 7. Nginx

```bash
sudo cp ~/improvpl/deploy/nginx/improvpl.conf /etc/nginx/sites-available/improvpl
sudo ln -s /etc/nginx/sites-available/improvpl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL (Certbot)

Point your domain A record to the droplet IP, then:

```bash
sudo certbot --nginx -d improv.pl -d www.improv.pl
```

### 9. Cron — close polls daily

```bash
crontab -e
```

Add (see `deploy/crontab.example`):

```
0 9 * * * /home/improvuser/improvpl/venv/bin/python /home/improvuser/improvpl/manage.py close_polls >> /var/log/improvpl_cron.log 2>&1
```

### 10. DNS

At your registrar (e.g. Namecheap):

| Type | Host | Value |
|------|------|-------|
| A | @ | DROPLET_IP |
| A | www | DROPLET_IP |

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