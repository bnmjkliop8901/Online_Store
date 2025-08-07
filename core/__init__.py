from .celery import app as celery_app

#To activate celery when django starts
__all__ = ["celery_app"]
