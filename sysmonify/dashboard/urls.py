"""urls.py.

URL routing configuration for the dashboard app.
"""

from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("processes/", views.processes_view, name="processes"),
    path("memory/", views.memory_view, name="memory"),
    path("gpu/", views.gpu_view, name="gpu"),
    path("network/", views.network_view, name="network"),
]
