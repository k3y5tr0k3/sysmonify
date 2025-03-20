"""apps.py.

Application configuration for process app.
"""

from django.apps import AppConfig


class ProcessConfig(AppConfig):
    """Application configuration class for process app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "process"
