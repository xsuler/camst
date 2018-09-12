from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import campip.routing
from campip.consumers import AlarmConsumer

application = ProtocolTypeRouter({
    'websocket':
    AuthMiddlewareStack(URLRouter(campip.routing.websocket_urlpatterns)),
})
