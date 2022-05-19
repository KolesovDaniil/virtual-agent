from django.test import TestCase

from pytest import fixture
from users.tests import UserFactory
from django.urls import reverse
from funcy import lmap

MOCKED_RETURN_VALUE = {}


@fixture
def mocked_moodle_api(mocker):
    mocker.patch('virtual_agent.moodle.moodle_api')


class TestUsersViewSet:
    def test_get_users(self, mocked_moodle_api, client):
        mocked_moodle_api.return_value = MOCKED_RETURN_VALUE
        users = UserFactory.create_batch(size=3)
        url = reverse('api:users-list')

        response = client.get(url)

        assert response.json() == api_response(lmap(serialize_user, users))


def serialize_user(user):
    pass


def api_response(_):
    pass


