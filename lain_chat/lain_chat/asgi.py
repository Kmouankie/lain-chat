import os
import django
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lain_chat.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

django_asgi_app = get_asgi_application()

from security.middleware import WebSocketSecurityMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": WebSocketSecurityMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})