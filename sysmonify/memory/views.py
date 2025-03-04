"""views.py.

Views for the memory app.
"""

from django.views.generic import TemplateView


class MemoryView(TemplateView):
    """Memory real-time metrics view."""

    template_name = "memory.html"
