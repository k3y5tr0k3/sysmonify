"""urls.py.

URL routing configuration for the dashboard app.
"""

from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("processes/", views.processes_view, name="processes"),
]
