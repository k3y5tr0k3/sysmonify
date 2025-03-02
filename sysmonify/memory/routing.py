"""routing.py.

Routing configuration for memory app channels.
"""

from django.urls import re_path
from memory import consumers

websocket_urlpatterns = [
    re_path(r"ws/memory/", consumers.MemoryConsumer.as_asgi()),
]
