"""views.py.

Views for the disk app.
"""

from django.views.generic import TemplateView


class DisksView(TemplateView):
    """Disks real-time metrics view."""

    template_name = "disks.html"
