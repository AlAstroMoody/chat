from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.core.exceptions import ValidationError

from apps.users.errors import StudentError
from ..errors import RoomError
from ..models import Room


class Chat:
    @staticmethod
    @database_sync_to_async
    def validate_room(uuid, user):
        try:
            room = Room.objects.get(connection_uuid=uuid)
        except (ValidationError, Room.DoesNotExist):
            raise DenyConnection({'error': RoomError.ROOM_NOT_FOUND})
        if room.is_finished:
            raise DenyConnection({'error': StudentError.TRAINING_IS_FINISHED})
        if user.is_trainer:
            if room.trainer != user:
                raise DenyConnection({'error': StudentError.NO_ACCESS})
        else:
            if user.student.connection_uuid != room:
                raise DenyConnection({'error': StudentError.NO_ACCESS})
            if user.student.is_kicked:
                raise DenyConnection({'error': StudentError.YOU_WAS_KICKED})
