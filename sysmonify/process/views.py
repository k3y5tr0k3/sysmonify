"""views.py.

Views for process app.
"""

from django.views.generic import TemplateView


class ProcessView(TemplateView):
    """Template view for process app."""

    template_name = "process.html"
