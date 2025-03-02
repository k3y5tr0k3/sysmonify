"""urls.py.

URL routing configuration for the memory app.
"""

from django.urls import path
from memory import views

urlpatterns = [
    path("memory/", views.MemoryView.as_view(), name="memory"),
]
