from collections import namedtuple
from datetime import datetime

from .. import fields, manager, model
from ..interaction import GenericInteraction

TEXT = "text"  # Текст
NUMERIC = "numeric"  # Число
CHECKBOX = "checkbox"  # Флаг
SELECT = "select"  # Список
MULTISELECT = "multiselect"  # Мультисписок
DATE = "date"  # Дата
URL = "url"  # Ссылка
TEXTAREA = "textarea"  # Текстовая область
RADIOBUTTON = "radiobutton"  # Переключатель
STREET_ADDRESS = "streetaddress"  # Короткий адрес
DATETIME = "date_time"  # Дата и время

MULTITEXT = "multitext"
# smart_address	Адрес
# birthday	День рождения
# legal_entity	Юр. лицо
# PRICE  = "price" # Цена
# CATEGORY = "category" # Категория
# ITEMS = "items"  # Предметы


class SelectValue:
    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value


class _FieldsRegisterMeta(type):
    _REGISTER = {}

    def __new__(cls, name, bases, dct):
        _class = super().__new__(cls, name, bases, dct)
        cls._REGISTER[(_class.type, _class._real_code)] = name
        return _class


def _get_field_class(type_name, code) -> str:
    get = _FieldsRegisterMeta._REGISTER.get
    return get((type_name, code), get((type_name, None), "BaseCustomField"))


class CustomFieldModel(model.Model):
    name = fields._Field("name")
    code = fields._Field("code", blank=True)
    sort = fields._Field("sort")
    type = fields._Field("type")
    entity_type = fields._Field("entity_type")

    is_deletable = fields._Field("is_deletable", blank=True)
    is_api_only = fields._Field("is_api_only", blank=True)

    enums = fields._Field("enums", blank=True)

    @classmethod
    def get_for(cls, instance):
        return manager.Manager(
            GenericInteraction(path=f"{instance._path}/custom_fields", field="custom_fields",), model=CustomFieldModel,
        ).all()

    @classmethod
    def create_for(cls, instance, name, code=None, sort=None):
        return (
            manager.Manager(
                GenericInteraction(path=f"{instance._path}/custom_fields", field="custom_fields",),
                model=CustomFieldModel,
            )
            .create(name=name, code=code, sort=sort,)
            .code
        )


class BaseCustomField(fields._BaseField, metaclass=_FieldsRegisterMeta):
    _real_code = None
    type = None

    def __init__(self, name, code=None, auto_create=False, field_id=None, **kwargs):
        super().__init__("custom_fields_values", blank=True)
        self._name = name
        self._create_with = kwargs
        self._code = self._real_code or code
        self._field_id = field_id
        self._auto_create = auto_create

    def _find(self, instance):
        for field in CustomFieldModel.get_for(instance):
            if field.name == self._name or (self._code and self._code == field.code):
                return field
        return None

    def _check(self, instance):
        if self._field_id:
            return
        field = self._find(instance)
        if field:
            self._code = field.code
            self._field_id = field.id
        # if self._real_code is None and self._auto_create:
        #     self._real_code = CustomFieldModel.create_for(
        #         instance=instance,
        #         name=self._name,
        #         code=self._code,
        #         type=self.type,
        #         **self._create_with,
        #     )
        #     return
        # raise Exception("Field does not exists")

    def on_get_instance(self, instance, data):
        if data is None:
            return
        field_data = self._get_raw_field(data)
        if field_data:
            return self.on_get(field_data["values"])

    def _get_raw_field(self, data):
        if data is None:
            return None
        for field in data:
            if field.get("field_name", "error") == self._name:
                return field
            if self._code and field.get("field_code") == self._code:
                return field
        return None

    def _create_raw_field(self):
        _data = {"field_id": self._field_id, "values": []}
        if self._code:
            _data["field_code"] = self._code
        if self._name:
            _data["field_name"] = self._name
        return _data

    def __set__(self, instance, value):
        if instance is None or value is None:
            return
        data = instance._data
        for _path in self._path:
            data = data.setdefault(_path, {self.name: []})
        _data = self._get_raw_field(data.get(self.name))
        if _data is None:
            self._check(instance)
            if data.get(self.name) is None:
                data[self.name] = []
            data.setdefault(self.name, []).append(self._create_raw_field())
            _data = self._get_raw_field(data.get(self.name))
        values = self.on_set_instance(_data["values"], value)

        _data["values"] = values
        self._notify_instance(instance)
        return values


class TextCustomField(BaseCustomField):
    type = TEXT

    def on_get(self, values):
        return values[0]["value"]

    def on_set(self, value):
        return [{"value": value}]


class TextAreaCustomField(TextCustomField):
    type = TEXTAREA


class UrlCustomField(TextCustomField):
    type = URL


class StreetAddressCustomField(TextCustomField):
    type = STREET_ADDRESS


class SelectCustomField(TextCustomField):
    type = SELECT

    def __init__(self, *args, enums=None, **kwargs):
        # kwargs["enums"] = [{"value": enums[i], "sort": i + 1} for i in range(len(enums))]
        super().__init__(*args, **kwargs)

    def on_get(self, values):
        return SelectValue(id=values[0]["enum_id"], value=values[0]["value"])

    def on_set(self, value):
        if isinstance(value, SelectValue):
            return [{"value": value.value, "enum_id": value.id}]
        return [{"value": value}]


class RadioButtonCustomField(SelectCustomField):
    type = RADIOBUTTON


class MultiSelectCustomField(SelectCustomField):
    type = MULTISELECT

    def on_get(self, values):
        return [SelectValue(id=item["enum_id"], value=item["value"]) for item in values]

    def on_set(self, values):
        if values and isinstance(values[0], SelectValue):
            return [{"value": value.value, "enum_id": value.id} for value in values]
        return [{"value": value} for value in values]


class NumericCustomField(TextCustomField):
    type = NUMERIC

    def on_get(self, values):
        return float(values[0]["value"])


class CheckboxCustomField(TextCustomField):
    type = CHECKBOX

    def on_get(self, values):
        return bool(values[0]["value"])


class DateCustomField(TextCustomField):
    type = DATE

    def on_get(self, values):
        return datetime.fromtimestamp(values[0]["value"]).date()

    def on_set(self, value):
        if isinstance(value, datetime):
            value = value.timestamp()
        return super().on_set(value)


class DateTimeCustomField(DateCustomField):
    type = DATETIME

    def on_get(self, values):
        return datetime.fromtimestamp(values[0]["value"])


class ContactPhoneField(TextCustomField):
    type = MULTITEXT
    _real_code = "PHONE"

    def __init__(self, *args, enum_code="WORK", **kwargs):
        self._enum_code = enum_code
        super().__init__(*args, **kwargs)

    def on_get(self, values):
        for value in values:
            if value["enum_code"] == self._enum_code:
                return value["value"]

    def on_set_instance(self, values, value):
        for item in values:
            if item["enum_code"] == self._enum_code:
                item["value"] = value
                return values
        values.append({"enum_code": self._enum_code, "value": value})
        return values


class ContactEmailField(ContactPhoneField):
    type = MULTITEXT
    _real_code = "EMAIL"
