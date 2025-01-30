"""views.py.

Views for the CPU app.
"""

from django.views.generic import TemplateView


class CpuView(TemplateView):
    """CPU real-time metrics view."""

    template_name = "cpu.html"
