from rest_framework.generics import CreateAPIView

from ..permissions import IsTrainer
from ..serializers import RoomSerializer


class RoomView(CreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = (IsTrainer,)
