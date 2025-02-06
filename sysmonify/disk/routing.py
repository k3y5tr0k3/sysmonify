"""routing.py.

Routing configuration for disk app channels.
"""

from django.urls import re_path
from disk import consumers

websocket_urlpatterns = [
    re_path(r"ws/disks/", consumers.DiskConsumer.as_asgi()),
]
