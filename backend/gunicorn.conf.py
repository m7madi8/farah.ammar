"""
Gunicorn config for Nana's Bites backend.
Run: gunicorn config.wsgi:application -c gunicorn.conf.py
"""
import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
worker_class = "sync"
worker_connections = 1000
max_requests = 1200
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nanas_bites"

# Don't capture for local dev (see stack traces in console)
capture_output = False
