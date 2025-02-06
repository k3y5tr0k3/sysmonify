"""views.py.

A module containing views for the dashboard app.
"""

from django.shortcuts import render


def index_view(request):
    """Dashboard overview view."""
    return render(request, "index.html")


def processes_view(request):
    """Processes view."""
    return render(request, "processes.html")


def memory_view(request):
    """Memory view."""
    return render(request, "memory.html")


def gpu_view(request):
    """GPU view."""
    return render(request, "gpu.html")


def network_view(request):
    """Network view."""
    return render(request, "network.html")
