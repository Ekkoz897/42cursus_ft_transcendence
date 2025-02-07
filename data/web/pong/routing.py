from django.urls import path
from .pong import SinglePongConsumer, QuickLobby

websocket_urlpatterns = [
    path('ws/spong/', SinglePongConsumer.as_asgi()),
    path('ws/mpong/', QuickLobby.as_asgi())
]