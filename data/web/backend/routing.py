from django.urls import path
from .pong import pong

websocket_urlpatterns = [
    path('ws/spong/', pong.SinglePongConsumer.as_asgi()),
	path('ws/mpong/', pong.QuickLobby.as_asgi()),
]