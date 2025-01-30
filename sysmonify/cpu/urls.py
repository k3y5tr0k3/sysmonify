"""urls.py.

URL routing configuration for the dashboard app.
"""

from django.urls import path
from cpu import views

urlpatterns = [
    path("cpu/", views.CpuView.as_view(), name="cpu"),
]
