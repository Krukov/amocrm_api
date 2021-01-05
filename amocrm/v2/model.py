import inspect

from . import fields
from .register import _RegisterMeta

_EMBEDDED_FIELDS = (fields._EmbeddedLinkListField, fields._EmbeddedLinkField)
_FIELDS_FOR_REPR = (fields._Field,) + _EMBEDDED_FIELDS


class Model(metaclass=_RegisterMeta):
    _init_data = {}
    id = fields._UnEditableField("id", blank=True)

    def __init__(self, data=None, **kwargs):
        self._data = data or {}
        self._data.update(self._init_data)
        self._updated_fields = set()
        attribs = kwargs.copy()

        for attr, value in attribs.items():
            if isinstance(getattr(self.__class__, attr), fields._BaseField):
                kwargs.pop(attr)
                setattr(self, attr, value)
        if kwargs:
            raise ValueError("Wrong attributes {}".format(list(kwargs.keys())))

    @property
    def _path(self):
        return self._manager._interaction.path

    @classmethod
    def _get_embedded_fields(cls):
        return [
            field.name
            for _, field in inspect.getmembers(cls)
            if isinstance(field, fields._BaseField) and field.is_embedded
        ]

    def __repr__(self):
        fields = [
            "{} = {}".format(field.name, getattr(self, attr))
            for attr, field in inspect.getmembers(self.__class__)
            if isinstance(field, _FIELDS_FOR_REPR)
        ]
        return "{self.__class__.__name__}({fields})".format(self=self, fields=", ".join(fields))

    def save(self):
        if self.id:
            self.update()
        else:
            self.create()
        return self

    @property
    def _manager(self):
        return self.__class__.objects

    def create(self):
        self._data["id"] = self._manager.create(self._data).id

    def update(self):
        if self._updated_fields:
            self._manager.update(self.id, self._get_updated_data())
            self._updated_fields = set()

    def _get_updated_data(self):
        data = {}
        for field_path in self._updated_fields:
            data.update(_get_container_by_path(field_path, self._data))
        return data


def _get_container_by_path(path, data):
    container = {}
    if not path:
        return data
    container[path[0]] = _get_container_by_path(path[1:], data[path[0]])
    return container
