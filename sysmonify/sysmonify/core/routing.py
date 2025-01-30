"""routing.py.

Routing configuration for sysmonify.core app channel for testing purposes.
"""

from django.urls import re_path
from sysmonify.core import consumers

websocket_urlpatterns = [
    re_path(r"ws/test/$", consumers.TestConsumer.as_asgi()),
]
