"""ASGI config for sysmonify project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from dashboard.routing import websocket_urlpatterns as dashboard_websocket_urlpatterns
from sysmonify.core.routing import websocket_urlpatterns as test_websocket_urlpatterns
from cpu.routing import websocket_urlpatterns as cpu_websocket_urlpatterns
from disk.routing import websocket_urlpatterns as disk_websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sysmonify.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                dashboard_websocket_urlpatterns
                + test_websocket_urlpatterns
                + cpu_websocket_urlpatterns
                + disk_websocket_urlpatterns
            )
        ),
    }
)
