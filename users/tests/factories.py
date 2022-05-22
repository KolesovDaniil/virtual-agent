import factory

from ..models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user#{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')

    class Meta:
        model = User
