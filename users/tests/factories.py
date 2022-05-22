import factory.fuzzy

from ..models import Group, TeachersPositions, User, UserTypes


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('slug')

    class Meta:
        model = Group


class StudentFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'student#{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    group = factory.SubFactory(GroupFactory)
    type = UserTypes.STUDENT

    class Meta:
        model = User


class LecturerFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'lecturer#{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    position = factory.fuzzy.FuzzyChoice(TeachersPositions.values())
    type = UserTypes.LECTURER

    class Meta:
        model = User
