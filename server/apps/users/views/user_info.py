from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from ..serializers.user_info import UserInfoSerializer


class UserInfoView(RetrieveAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
