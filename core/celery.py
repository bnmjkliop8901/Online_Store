import os
from celery import Celery

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Create the Celery app instance
app = Celery("core")

# Load Celery config from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks in installed apps
app.autodiscover_tasks()
