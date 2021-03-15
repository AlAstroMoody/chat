import factory

from apps.rooms.models import Room
from apps.tests.factories.user import UserFactory


class RoomFactory(factory.Factory):
    class Meta:
        model = Room

    trainer = factory.SubFactory(UserFactory)
    max_round_time = Room.Constraints.MAX_ROUND_TIME
    max_rounds_count = Room.Constraints.MIN_ROUNDS_COUNT
    max_students_count = Room.Constraints.MAX_STUDENTS_COUNT
    is_started = False
    is_finished = False
