# Nana's Bites — Monitoring and Logging

## Logging

- **Django:** `config.settings.LOGGING` — console always; in production: rotating file at `logs/django.log` (when `logs/` exists) and email to `ADMINS` on ERROR (when `ADMINS` and email are set).
- **App loggers:** `orders`, `products` — use at INFO for important events (order created, payment confirmed, stock updated).
- **Gunicorn:** Access and error logs via `GUNICORN_ACCESS_LOG` / `GUNICORN_ERROR_LOG` or systemd journal. Access format includes response time (`%D` μs).

## Sentry

Set `SENTRY_DSN` in production to report exceptions and optional performance traces.

- Optional: `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE` (default 0.1).

## Email alerts

Set `ADMINS` (e.g. `"Name,admin@domain.com"`) and `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `SERVER_EMAIL`. Django will email ADMINS on 500 errors and when `logger.error()` is used (if mail handler is configured).

## Response times and uptime

- Use Nginx access log or a reverse-proxy metric exporter for response times.
- External uptime checks (e.g. UptimeRobot, Pingdom) on `https://api.yourdomain.com/api/products/` (expect 200).

## Optional: Prometheus / Grafana

- Add `django-prometheus` and expose `/metrics` behind admin-only or a dedicated scrape URL.
- Grafana dashboards can show request rate, latency, and DB connections.
