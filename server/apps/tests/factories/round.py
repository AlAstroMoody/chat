import factory

from apps.rooms.models import Round
from apps.tests.factories import RoomFactory


class RoundFactory(factory.Factory):
    class Meta:
        model = Round

    room = factory.SubFactory(RoomFactory)
