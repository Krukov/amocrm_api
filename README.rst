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

Авторизация - с Июня 2020 amoCRM форсировала смену авторизации с токена на OAuth

И без поддержки server to server взаимодействия, в связи с чем текущая реализация содержит следующие ограничения

1. В личном кабинете необходимо создать интеграцию
2. Рефреш токен одноразовый и обновляется при каждом получении аксесс токена
3. Ecли запросы в amoCRM происходят реже чем время жизни рефреш токена то вам не подойдет такой варант интеграции
4. Токены нужно хранить, для этого есть api и существует 3 типа хранилища (можно реализовать свой):

- MemoryTokensStorage - хранит токены в памяти (если вы перезапускаете приложение то придется снова создавать refresh_token)
- FileStorage - сохраняет токены в файле
- RedisTokensStorage - сохраняет токены в редисе (pip install redis) для new-age приложений которые работают в нескольких экземплярах

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
- Примечание - Note
- Событие - Event
- Воронки и Статусы - Pipeline, Status

Работа с сущностями
--------------------

У каждой сущности есть менеджер (аттрибут objects), который имеет следующие методы

::

    <Entity>.objects.get(object_id=1, query="test")  # получение обьекта
    <Entity>.objects.all()  # получение всех сущностей
    <Entity>.objects.filter(**kwargs)  # получение списка сущностей с фильтром

    <Entity>.objects.create(**kwargs)  # создание сущности (нет явной сигнатуры поэтому лучше использовать метод create самой сущности)
    <Entity>.objects.update(**kwargs)  # обносление сущности (нет явной сигнатуры поэтому лучше использовать метод update самой сущности)

В свою очередь сама сущность имеет несколько методов для более простого создания и обновления

::

    <EntityInstance>.create()
    <EntityInstance>.update()
    <EntityInstance>.save()  # создаст или обновит в зависимости от того как обьект был инициализирован

Исключение - создание звонка происходит через упрошенную сущность
::

    from amocrm.v2 import Call, CallDirection, CallStatus

    Call().create(CallDirection.OUTBOUNT, phone="....", source="", duration=timedelta(minutes=10), status=CallStatus.CALL_LATER, created_by=manager)


Рассмотрим полный процесс работы на примере контакта

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

    contact.company = Company(name="Amocrm")  # создаст и сразу прилинкует компанию
    print(contact.company.id)

    len(list(contact.customers)) # lazy list
    contact.customers.append(Customer(name="Volta"))


Кастомные поля
--------------

Одна из удобных возможностей amoCRM  - кастомные поля

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

Для ее работы необходимо установить пакет python-slugify (https://github.com/un33k/python-slugify)
