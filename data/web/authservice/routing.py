from django.urls import path
from .consumers import LoginMenuConsumer

auth_websocket_urlpatterns = [
    path('wss/login-menu/', LoginMenuConsumer.as_asgi()),
]