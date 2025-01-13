"""urls.py.

URL routing configuration for the dashboard app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("processes/", views.processes_view, name="processes"),
    path("cpu/", views.cpu_view, name="cpu"),
    path("memory/", views.memory_view, name="memory"),
    path("gpu/", views.gpu_view, name="gpu"),
    path("network/", views.network_view, name="network"),
    path("io/", views.io_view, name="io"),
]
