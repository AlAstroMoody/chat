from django.urls import path

from .views import RoomView
from .views import ReportView

rooms_urlpatterns = [
    path('room/', RoomView.as_view(), name='room'),
    path('room/<uuid:uuid>-<str:token>/report/', ReportView.as_view(), name='report'),
]
