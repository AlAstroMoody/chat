from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/room/<str:uuid>/', consumers.ChatConsumer),
]
