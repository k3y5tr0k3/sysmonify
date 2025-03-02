"""app.py.

Application configuration for the memory app.
"""

from django.apps import AppConfig


class MemoryConfig(AppConfig):
    """Application configuration class for the memory app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "memory"
