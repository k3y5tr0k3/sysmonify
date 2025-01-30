"""app.py.

Application config for the CPU app.
"""

from django.apps import AppConfig


class CpuConfig(AppConfig):
    """Application configuration class for the CPU app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "cpu"
