"""views.py.

A module containing views for the dashboard app.
"""

from django.shortcuts import render


def index_view(request):
    """Dashboard overview view."""
    return render(request, "index.html")
