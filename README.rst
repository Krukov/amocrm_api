===============================
AmoCRM python API. V2
===============================

.. image:: https://travis-ci.org/Krukov/amocrm_api.svg?branch=master
    :target: https://travis-ci.org/Krukov/amocrm_api
.. image:: https://img.shields.io/coveralls/Krukov/amocrm_api.svg
    :target: https://coveralls.io/r/Krukov/amocrm_api


Python AmoCRM API v2 (http://www.amocrm.ru/) (human interface for easy using)


Installation
============

::

    pip install amocrm_api

Usage
=====

Авторизация
-----------

Авторизация - с Июня 2020 amocrm форсировала смену авторизации с токена на Oauth
Но Oauth без поддержки server to server взаимодействия, связи с чем текущая реализация содержит следующие ограничения
1. В личном кабинете необходимо создать интеграцию
2. Рефрешь токен однаразовый и обновляется при каждом получении аксесс токена
3. Токены нужно хранить, для этого есть api и существует 3 типа хранилиша (можно реализовать свой):

- MemoryTokensStorage - хранит токены в памяти (если вы перезапускаете приложение то придется стнова создавать refresh_token)
- FileStorage - сохраняет токены в файле
- RedisTokensStorage - сохраняет токены в редисе (pip install redis) для new-age приложений каторые работают в нескольок инстансов

Example::

    from amocrm.v2 import tokens

    tokens.default_token_manager(
        client_id="xxx-xxx-xxxx-xxxx-xxxxxxx",
        client_secret="xxxx",
        subdomain="subdomain",
        redirect_url="https://xxxx/xx",
        storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
    )
    tokens.default_token_manager.init(code="..very long code...", skip_error=True)


- Контакт - Contact
- Компания  - Company
- Теги - Tags
- Сделка - Lead
- Задача - Task
- Событие - Note


Работа с сушьностями
--------------------

У каждой сущности есть менеджер (проперти objects), который имеет следующие методы

::

    <Entity>.objects.get(object_id=1, query="test")  # получение обьекта
    <Entity>.objects.all()  # получение всех сущьностей
    <Entity>.objects.filter(**kwargs)  # получение списка сущьностей с фильтром

    <Entity>.objects.create(**kwargs)  # создание сущьности (нет явной сигнатуры поэтому лучше испольщовать метод create самой сушьности)
    <Entity>.objects.update(**kwargs)  # обносление сущьности (нет явной сигнатуры поэтому лучше испольщовать метод update самой сушьности)

В свою очередь сама сушьность имеет несколько методов для более простого создания и обноления

::

    <EntityInstance>.create()
    <EntityInstance>.update()
    <EntityInstance>.save()  # создаст или обновит в зависимости от того как обьект был инициализирован

Исключение - зоздание звонка происходит через упрошенную сущьность
::

    from amocrm.v2 import Call, CallDirection, CallStatus

    Call().create(CallDirection.OUTBOUNT, phone="....", source="", duration=timedelta(minutes=10), status=CallStatus.CALL_LATER, created_by=manager)


Рассмотрим полный флоу работы на примере контакта

::

    from amocrm.v2 import Contact, Company

    contact = Contact.objects.get(query="Тест")
    print(contact.first_name)
    print(contact.company.name)
    print(contact.created_at)

    contact.last_name = "Новое"
    contact.tags.append("new")
    contact.notes.objects.create(text="Примечание")

    contact.save()

    contact.company = Company(name="Amocrm")  # создаст и приленкует компанию сразу
    print(contact.company.id)

    len(list(contact.customers)) # lazy list
    contact.customers.append(Customer(name="Volta"))


Кастомные поля
--------------

Одна из удобных возможностей AmoCrm  - кастомные поля

Example::

    from amocrm.v2 import Lead as _Lead, custom_field

    class Lead(_Lead):
        utm = custom_field.UrlCustomField("UTM метка")
        delivery_type = custom_field.SelectCustomField("Способ доставки")
        address = custom_field.TextCustomField("Адрес")


Однако мапинг всех кастомных полей дело утоминетльное,
поэтому для генерации файла с готовым мапингом есть команда::

    export AMOCRM_CLIENT_ID=xxx
    export AMOCRM_SECRET=xxx
    export AMOCRM_SUBDOMAIN=xxx
    export AMOCRM_REDIRECT_URL=xxx
    export AMOCRM_CODE=xxx # optional
    pyamogen > models.py
