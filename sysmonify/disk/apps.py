"""app.py.

Application configuration for disk app.
"""

from django.apps import AppConfig


class DiskConfig(AppConfig):
    """Application configuration class for disk app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "disk"
