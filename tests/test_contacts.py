import pytest

from amocrm.v2 import Contact, exceptions

from .data.companies import DETAIL_INFO as COMPANY_DETAIL_INFO
from .data.contacts import (CREATE_DATA, DETAIL_INFO, LIST_PAGE_1, LIST_PAGE_2,
                            UPDATE)
from .data.users import DETAIL_INFO as USER_DETAIL_INFO


def test_get(response_mock):
    response_mock.add("GET", "https://test.amocrm.ru/api/v4/contacts/3", match_querystring=False, json=DETAIL_INFO)
    contact = Contact.objects.get(3)

    assert contact.id == 3
    assert contact.name == "Иван Иванов"
    assert contact.first_name == "Иван"
    assert contact.last_name == "Иванов"

    response_mock.add("GET", "https://test.amocrm.ru/api/v4/users/3", match_querystring=False, json=USER_DETAIL_INFO)
    assert contact.responsible_user.id == 3
    assert contact.responsible_user.name == "Алексей Поимцев"

    response_mock.add(
        "GET", "https://test.amocrm.ru/api/v4/companies/1", match_querystring=False, json=COMPANY_DETAIL_INFO
    )
    assert contact.company.name == "АО Рога и копыта"
    assert contact.company.account_id == 10


def test_get_not_found(response_mock):
    response_mock.add("GET", "https://test.amocrm.ru/api/v4/contacts/3", match_querystring=False, status=204)
    with pytest.raises(exceptions.NotFound):
        Contact.objects.get(3)


def test_list(response_mock):
    response_mock.add(
        "GET", "https://test.amocrm.ru/api/v4/contacts", match_querystring=False, status=200, json=LIST_PAGE_1
    )
    response_mock.add(
        "GET", "https://test.amocrm.ru/api/v4/contacts", match_querystring=False, status=200, json=LIST_PAGE_2
    )

    contacts = list(Contact.objects.all())
    assert len(contacts) == 3
    assert contacts[0].name == "1"


def test_create(response_mock):
    response_mock.add("POST", "https://test.amocrm.ru/api/v4/contacts", status=200, json=CREATE_DATA)
    c = Contact(name="test", responsible_user=3, tags=[])
    c.save()
    assert c.id == 3


def test_update(response_mock):
    response_mock.add("GET", "https://test.amocrm.ru/api/v4/contacts/3", match_querystring=False, json=DETAIL_INFO)
    response_mock.add("PATCH", "https://test.amocrm.ru/api/v4/contacts/3", match_querystring=False, json=UPDATE)

    contact = Contact.objects.get(3)
    contact.last_name = "e"
    contact.tags.add("tag")
    contact.save()
