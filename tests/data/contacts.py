DETAIL_INFO = {
    "id": 3,
    "name": "Иван Иванов",
    "first_name": "Иван",
    "last_name": "Иванов",
    "responsible_user_id": 3,
    "group_id": 0,
    "created_by": 3,
    "updated_by": 504141,
    "created_at": 1582117331,
    "updated_at": 1590943929,
    "closest_task_at": None,
    "custom_fields_values": [
        {
            "field_id": 3,
            "field_name": "Телефон",
            "field_code": "PHONE",
            "field_type": "multitext",
            "values": [{"value": "+79123", "enum_id": 1, "enum": "WORK"}],
        }
    ],
    "account_id": 28805383,
    "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/3"}},
    "_embedded": {
        "tags": [],
        "leads": [
            {"id": 1, "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/leads/1"}}},
            {"id": 3916883, "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/leads/3916883"}}},
        ],
        "customers": [
            {"id": 134923, "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/customers/134923"}}}
        ],
        "catalog_elements": [],
        "companies": [{"id": 1, "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/companies/1"}}}],
    },
}

LIST_PAGE_1 = {
    "_page": 1,
    "_links": {
        "self": {"href": "https://example.amocrm.ru/api/v4/contacts?limit=2&page=1"},
        "next": {"href": "https://example.amocrm.ru/api/v4/contacts?limit=2&page=2"},
    },
    "_embedded": {
        "contacts": [
            {
                "id": 7143599,
                "name": "1",
                "first_name": "",
                "last_name": "",
                "responsible_user_id": 504141,
                "group_id": 0,
                "created_by": 504141,
                "updated_by": 504141,
                "created_at": 1585758065,
                "updated_at": 1585758065,
                "closest_task_at": None,
                "custom_fields_values": None,
                "account_id": 28805383,
                "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/7143599"}},
                "_embedded": {"tags": [], "companies": []},
            },
            {
                "id": 7767065,
                "name": "dsgdsg",
                "first_name": "",
                "last_name": "",
                "responsible_user_id": 504141,
                "group_id": 0,
                "created_by": 504141,
                "updated_by": 504141,
                "created_at": 1586359590,
                "updated_at": 1586359590,
                "closest_task_at": None,
                "custom_fields_values": None,
                "account_id": 28805383,
                "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/7767065"}},
                "_embedded": {"tags": [], "companies": []},
            },
        ]
    },
}

LIST_PAGE_2 = {
    "_page": 2,
    "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts?limit=2&page=2"},},
    "_embedded": {
        "contacts": [
            {
                "id": 7143599,
                "name": "1",
                "first_name": "",
                "last_name": "",
                "responsible_user_id": 504141,
                "group_id": 0,
                "created_by": 504141,
                "updated_by": 504141,
                "created_at": 1585758065,
                "updated_at": 1585758065,
                "closest_task_at": None,
                "custom_fields_values": None,
                "account_id": 28805383,
                "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/7143599"}},
                "_embedded": {"tags": [], "companies": []},
            },
        ]
    },
}

CREATE_DATA = {
    "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts"}},
    "_embedded": {
        "contacts": [
            {
                "id": 3,
                "request_id": "0",
                "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/40401635"}},
            },
        ]
    },
}

UPDATE = {
    "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts"}},
    "_embedded": {
        "contacts": [
            {
                "id": 3,
                "name": "Иван Иванов",
                "updated_at": 1590945248,
                "_links": {"self": {"href": "https://example.amocrm.ru/api/v4/contacts/3"}},
            }
        ]
    },
}
