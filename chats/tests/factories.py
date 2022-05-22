import factory

from users.tests.factories import GroupFactory, StudentFactory

from ..models import Chat, Message


class ChatFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('slug')
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = Chat


class MessageFactory(factory.django.DjangoModelFactory):
    text = factory.Faker('text')
    chat = factory.SubFactory(ChatFactory)
    user = factory.SubFactory(StudentFactory)

    class Meta:
        model = Message
