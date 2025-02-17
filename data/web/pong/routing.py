from django.urls import path
from .pong import SinglePongConsumer, MultiPongConsumer, QuickLobby

websocket_urlpatterns = [
    path('wss/spong/', SinglePongConsumer.as_asgi()),
    path('wss/mpong/', QuickLobby.as_asgi()),
	path('wss/mpong/game/<str:game_id>/', MultiPongConsumer.as_asgi())
]