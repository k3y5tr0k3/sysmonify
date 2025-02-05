"""urls.py.

URL routing configuration for the disk app.
"""

from django.urls import path
from disk import views

urlpatterns = [
    path("disks/", views.DisksView.as_view(), name="disks"),
]
