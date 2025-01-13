"""apps.py.

Configuration for dashboard app.
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """AppConfig for dashboard app.

    Attributes:
        default_auto_field (str):
            Default database row identifier type.

        name (str):
            Application name.
    """

    default_auto_field = "django.db.models.AutoField"
    name = "dashboard"
