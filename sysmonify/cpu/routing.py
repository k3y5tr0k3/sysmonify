"""routing.py.

Routing configuration for dashboard app channels.
"""

from django.urls import re_path
from cpu import consumers

websocket_urlpatterns = [
    re_path(r"ws/cpu/", consumers.CPUConsumer.as_asgi()),
]
