"""views.py.

Views for the GPU app.
"""

from django.views.generic import TemplateView


class GPUView(TemplateView):
    """GPU real-time metrics view."""

    template_name = "gpu.html"
