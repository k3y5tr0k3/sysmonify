"""urls.py.

URL routing configuration for the GPU app.
"""

from django.urls import path
from gpu import views

urlpatterns = [
    path("gpu/", views.GPUView.as_view(), name="gpu"),
]
