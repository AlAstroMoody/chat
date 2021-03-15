import factory

from apps.users.models import Student
from . import UserFactory, RoomFactory


class StudentFactory(factory.Factory):
    class Meta:
        model = Student

    base_user = factory.SubFactory(UserFactory)
    nickname = factory.Faker('name')
    connection_uuid = factory.SubFactory(RoomFactory)
