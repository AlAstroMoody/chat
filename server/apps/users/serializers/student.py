from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from ..errors import StudentError as Errors
from ..models import Student, User
from ..models.user import Role
from ...rooms.models import Room


class StudentSerializer(serializers.ModelSerializer):
    connection_uuid = serializers.UUIDField(
        error_messages={'invalid': Errors.INVALID_ROOM_ID}
    )
    token = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'nickname',
            'connection_uuid',
            'token'
        )
        extra_kwargs = {
            'token': {'read_only': True},
        }

    def validate_connection_uuid(self, connection_uuid):
        try:
            room = Room.objects.get(
                connection_uuid=connection_uuid
            )
        except Room.DoesNotExist:
            raise serializers.ValidationError({
                'error': Errors.INVALID_ROOM_ID
            })
        if room.is_started:
            raise serializers.ValidationError({
                'error': Errors.TRAINING_IS_STARTED
            })
        if room.is_finished:
            raise serializers.ValidationError({
                'error': Errors.TRAINING_IS_FINISHED
            })
        return connection_uuid

    def validate_nickname(self, nickname):
        connection_uuid = self.initial_data["connection_uuid"]
        username = Student.generate_username(
            nickname,
            connection_uuid
        )
        try:
            user = User.objects.get(
                username=username
            )
            student = Student.objects.get(
                base_user=user
            )
            if student.is_kicked:
                raise serializers.ValidationError({
                    'error': Errors.YOU_WAS_KICKED
                })
            raise serializers.ValidationError({
                'error': Errors.NICKNAME_ALREADY_USED
            })
        except User.DoesNotExist:
            return nickname

    def get_token(self, obj):
        user = User.objects.get(
            username=Student.generate_username(
                obj.nickname,
                obj.connection_uuid
            )
        )
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        return access

    def create(self, validated_data):
        nickname = validated_data['nickname']
        connection_uuid = validated_data['connection_uuid']
        room = Room.objects.get(
            connection_uuid=connection_uuid
        )
        user = User.objects.create(
            role=Role.STUDENT,
            username=Student.generate_username(
                nickname,
                connection_uuid
            ),
        )
        student = Student.objects.create(
            nickname=nickname,
            connection_uuid=room,
            base_user=user
        )
        return student
