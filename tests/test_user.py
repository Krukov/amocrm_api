import pytest

from amocrm.v2 import exceptions
from amocrm.v2.entity.user import User

from .data.users import DETAIL_INFO


def test_get(response_mock):
    response_mock.add("GET", "https://test.amocrm.ru/api/v4/users/3", match_querystring=False, json=DETAIL_INFO)
    user = User.objects.get(3)

    assert user.id == 3
    assert user.name == "Алексей Поимцев"
    assert user.email == "test@example.com"
    assert user.language == "ru"
    assert not user.is_admin
    assert user.is_active
