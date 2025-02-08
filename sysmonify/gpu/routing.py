"""routing.py.

Routing configuration for GPU app channels.
"""

from django.urls import re_path
from gpu import consumers

websocket_urlpatterns = [
    re_path(r"ws/gpu/", consumers.GPUConsumer.as_asgi()),
]
