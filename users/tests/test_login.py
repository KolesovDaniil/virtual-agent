from http import HTTPStatus

from django.urls import reverse
from pytest import fixture

from virtual_agent.tests.utils import error_response

from .factories import UserFactory


class UserLoginTestCase:
    url = reverse('api:user_login')

    @fixture(autouse=True)
    def setup(self):
        self.user = UserFactory.create()

    def test_login_with_invalid_credentials(self, client):
        data = {
            'username': 'non_existing_username',
            'password': 'non_existing_password',
        }

        response = client.post(self.url, data=data)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == error_response(
            code='not_authenticated', message='Authentication credentials are invalid'
        )

    def test_login_with_invalid_password(self, client):
        data = {'username': self.user.username, 'password': 'invalid_password'}

        response = client.post(self.url, data=data)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == error_response(
            code='not_authenticated', message='Authentication credentials are invalid'
        )

    def test_login_with_right_credentials(self, client):
        self.user.set_password('user_password')
        self.user.save()
        data = {'username': self.user.username, 'password': 'user_password'}

        response = client.post(self.url, data=data)

        assert response.status_code == HTTPStatus.OK
