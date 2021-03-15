from rest_framework import serializers

from ..models import User, Student
from ...rooms.models import Room


class UserInfoSerializer(serializers.ModelSerializer):
    connection_uuid = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'connection_uuid',
            'username',
            'role'
        )
        extra_kwargs = {
            'username': {'read_only': True},
            'role': {'read_only': True},
        }

    def get_connection_uuid(self, user):
        if user.is_trainer:
            room = Room.objects.get(trainer=user)
        else:
            student = Student.objects.get(base_user=user)
            room = student.connection_uuid
        if not room.is_finished:
            return room.connection_uuid
