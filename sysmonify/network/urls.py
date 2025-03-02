"""urls.py.

URL routing configuration for the network app.
"""

from django.urls import path
from network import views

urlpatterns = [
    path("network/", views.NetworkView.as_view(), name="network"),
]
