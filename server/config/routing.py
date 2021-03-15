from channels.routing import ProtocolTypeRouter, URLRouter

from apps.rooms import routing
from apps.rooms.auth_middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
