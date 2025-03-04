"""routing.py.

Routing configuration for dashboard app channels.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/overview/", consumers.DashboardConsumer.as_asgi()),
    re_path(r"ws/processes/", consumers.ProcessesConsumer.as_asgi()),
]
