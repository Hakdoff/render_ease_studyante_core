"""
ASGI config for ease_studyante_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ease_studyante_core.settings')
django.setup()


from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat import routing
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    }
)

ASGI_APPLICATION = 'ease_studyante_core.asgi.application'
