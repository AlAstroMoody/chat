from rest_framework import serializers

from ..errors import RoomError as Errors
from ..models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            'max_round_time',
            'max_rounds_count',
            'max_students_count'
        )

    def validate(self, attrs):
        try:
            room = Room.objects.get(
                trainer=self.context['request'].user,
                is_started=True,
                is_finished=False
            )
            raise serializers.ValidationError({
                'error': Errors.UNFINISHED_CHAMPIONSHIP.format(str(room.connection_uuid))
            })
        except Room.DoesNotExist:
            return attrs

    def create(self, validated_data):
        room = Room.objects.create(
            max_round_time=validated_data['max_round_time'],
            max_rounds_count=validated_data['max_rounds_count'],
            max_students_count=validated_data['max_students_count'],
            trainer=self.context['request'].user,
        )
        return room
