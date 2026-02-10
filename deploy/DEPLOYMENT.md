# Nana's Bites — Production Deployment

Backend (Django + Gunicorn) + Frontend (React build) on Ubuntu / DigitalOcean / AWS, with PostgreSQL and HTTPS (Let's Encrypt).

## 1. Server and PostgreSQL

### Ubuntu (e.g. 22.04)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12-venv python3-pip nginx postgresql postgresql-contrib certbot python3-certbot-nginx
```

### PostgreSQL: create DB and user

```bash
sudo -u postgres psql -c "CREATE USER nanas_bites_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE nanas_bites OWNER nanas_bites_user;"
sudo -u postgres psql -c "ALTER DATABASE nanas_bites SET timezone TO 'UTC';"
```

Use a strong password and store it in `.env` as `DB_PASSWORD`.

## 2. Deploy backend

```bash
sudo mkdir -p /var/www/nanas_bites
sudo chown $USER:$USER /var/www/nanas_bites
cd /var/www/nanas_bites

# Backend
git clone <your-repo> repo && mv repo/backend backend && rm -rf repo  # or copy files
cd backend
python3 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env: SECRET_KEY, DB_*, ALLOWED_HOSTS, CORS_ORIGINS, STRIPE_*, SECURE_SSL_REDIRECT=1, ADMINS, etc.

# Logs dir (for file logging in production)
mkdir -p logs

# Migrate and static
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 3. Gunicorn (systemd)

```bash
sudo cp /path/to/deploy/gunicorn.service.example /etc/systemd/system/nanas-bites.service
# Edit: User/Group, paths (WorkingDirectory, ExecStart, EnvironmentFile)
sudo systemctl daemon-reload
sudo systemctl enable nanas-bites
sudo systemctl start nanas-bites
sudo systemctl status nanas-bites
```

## 4. Deploy frontend (React)

On the same server or a separate one:

```bash
cd /var/www/nanas_bites
# Copy react-app or clone repo
cd react-app
npm ci
# Set VITE_API_BASE=https://api.yourdomain.com for build
export VITE_API_BASE=https://api.yourdomain.com
npm run build
sudo mkdir -p /var/www/nanas_bites/frontend
sudo cp -r dist/* /var/www/nanas_bites/frontend/
```

## 5. Nginx and HTTPS

1. Copy `deploy/nginx.conf.example` to `/etc/nginx/sites-available/nanas_bites`.
2. Replace `yourdomain.com` and `api.yourdomain.com` with your domains.
3. Enable site: `sudo ln -s /etc/nginx/sites-available/nanas_bites /etc/nginx/sites-enabled/`
4. Initially comment out the `listen 443` blocks and the `return 301` so Nginx can start on port 80.
5. Get certificates:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
   ```
6. Uncomment SSL server blocks and the HTTP→HTTPS redirect. Reload Nginx:
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

## 6. Environment variables (summary)

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Random 50+ char secret |
| `DJANGO_DEBUG` | `0` in production |
| `ALLOWED_HOSTS` | Comma-separated domains |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL |
| `CORS_ORIGINS` | Frontend origin(s) |
| `SECURE_SSL_REDIRECT` | `1` behind HTTPS |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe |
| `SENTRY_DSN` | Optional error tracking |
| `ADMINS`, `EMAIL_*` | Critical error emails |

## 7. Static and media

- Static: `python manage.py collectstatic` → served by Nginx from `STATIC_ROOT` (e.g. `/var/www/nanas_bites/staticfiles/`).
- Media (if added later): set `MEDIA_ROOT` and `MEDIA_URL`, create directory, add Nginx `location /media/`.

## 8. Logging and monitoring

- Gunicorn: access/error logs via `GUNICORN_ACCESS_LOG`, `GUNICORN_ERROR_LOG` (or systemd journal).
- Django: see `config/settings.py` LOGGING; file handler and email handler when `ADMINS` and `EMAIL_*` are set.
- Sentry: set `SENTRY_DSN` to enable error reporting.

## 9. Health check

```bash
curl -s -o /dev/null -w "%{http_code}" https://api.yourdomain.com/api/products/
# Expect 200
```

## 10. Optional: Docker Compose

See `docker-compose.yml` in project root for a self-contained backend + DB + (optional) frontend build.
