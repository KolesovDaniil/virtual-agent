from pytest import fixture
from rest_framework.test import APIClient


@fixture
def client():
    return APIClient()


@fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
