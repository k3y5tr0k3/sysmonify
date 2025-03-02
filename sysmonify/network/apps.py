"""apps.py.

Application configuration for network app.
"""

from django.apps import AppConfig


class NetworkConfig(AppConfig):
    """Application configuration class for the network app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "network"
