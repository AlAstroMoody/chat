import factory

from apps.rooms.models import Message
from apps.tests.factories import UserFactory, RoundFactory


class MessageFactory(factory.Factory):
    class Meta:
        model = Message

    author = factory.SubFactory(UserFactory)
    text = factory.Faker('text')
    in_round = factory.SubFactory(RoundFactory)
    is_selected = True
    created_at = factory.Faker('random_int')
