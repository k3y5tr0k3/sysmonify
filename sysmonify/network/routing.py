"""routing.py.

Routing configuration for network app channels.
"""

from django.urls import re_path
from network import consumers

websocket_urlpatterns = [
    re_path(r"ws/network/", consumers.NetworkConsumer.as_asgi()),
]
