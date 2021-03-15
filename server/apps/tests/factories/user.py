import factory

from apps.users.models import User
from apps.users.models.user import Role


class UserFactory(factory.Factory):
    class Meta:
        model = User

    role = Role.TRAINER
    username = factory.Faker('name')
