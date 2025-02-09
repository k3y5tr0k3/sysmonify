"""views.py.

Views for the network app.
"""

from django.views.generic import TemplateView


class NetworkView(TemplateView):
    """Network real-time metrics view."""

    template_name = "network.html"
