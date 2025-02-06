"""apps.py.

Application configuration module for the GPU app.
"""

from django.apps import AppConfig


class GpuConfig(AppConfig):
    """Application configuration class for the GPU app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "gpu"
