"""urls.py.

URL routing configuration for the process app.
"""

from django.urls import path
from process import views

urlpatterns = [
    path("processes/", views.ProcessView.as_view(), name="processes"),
]
