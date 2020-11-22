from datetime import datetime

from . import exceptions
from .links import LinksInteraction
from .register import get_model_by_name


class _BaseField:
    _path = []

    def __init__(self, name=None, blank=False, path=None, cache=False, is_embedded=None):
        self.name = name
        self._blank = blank
        self._path = path if path is not None else self._path
        self._cache = cache
        self.__value = None
        self.__is_embedded = is_embedded

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, blank={self._blank}, path={self._path})"

    def __hash__(self):
        return "{}:{}".format(self.name, ":".join(self._path))

    def __get__(self, instance, _=None):
        # TODO: cache for get and check set for difference
        if instance is None:
            return self
        data = instance._data
        for _path in self._path:
            data = data.get(_path, {})
        data = data.get(self.name)
        if data is None and not self._blank:
            raise exceptions.NoDataException(str(self))
        return self.on_get_instance(instance, data)

    def __set__(self, instance, value):
        if instance is None or value is None:
            return
        value = self.on_set_instance(instance, value)
        data = instance._data
        for _path in self._path:
            data = data.setdefault(_path, {})
        if self.name not in data or data[self.name] != value:
            data[self.name] = value
            self._notify_instance(instance)
        return value

    def _notify_instance(self, instance):
        instance._updated_fields.add((*self._path, self.name))

    def on_set_instance(self, instance, value):
        return self.on_set(value)

    def on_get_instance(self, instance, data):
        return self.on_get(data)

    def on_set(self, value):
        return value

    def on_get(self, data):
        return data

    @property
    def is_embedded(self):
        if self.__is_embedded is None:
            return bool(self._path and self._path[0] == "_embedded")
        return self.__is_embedded


class _Field(_BaseField):
    pass


class _UnEditableField(_Field):
    def __set__(self, instance, value):
        raise TypeError()


class _DateTimeField(_Field):
    def on_get(self, data):
        if data is not None:
            return datetime.utcfromtimestamp(float(data))

    def on_set(self, value):
        if isinstance(value, datetime):
            return value.timestamp()


class _ObjectField(_UnEditableField):
    def __init__(self, model, *args, many=False, **kwargs):
        self._model = model
        self._many = many
        super().__init__(*args, **kwargs)

    def on_get(self, data):
        if self._many:
            return [self._model.from_dict(**item) for item in data]
        return self._model.from_dict(**data)


class _Link(_BaseField):
    def __init__(self, name, model, links=LinksInteraction(), manager=None):
        super().__init__(name, blank=True)
        self.__model = model
        self._links = links
        self.__manager = manager

    @property
    def _model(self):
        if isinstance(self.__model, str):
            self.__model = get_model_by_name(self.__model)
        return self.__model

    @property
    def _manager(self):
        return self.__manager or self._model.objects

    def on_get(self, data):
        return self._manager.get(object_id=data)

    def on_set(self, value):
        if isinstance(value, self._model):
            return value.id
        return value


class _ListData:
    def __init__(self, data, instance, model, manager=None, links=LinksInteraction()):
        self._data = data
        self._model = model
        self._instance = instance
        self._manager = manager or model.objects
        self._links = links

    def __iter__(self):
        yield from (self._manager.get(item["id"]) for item in self._data)

    def append(self, value, main=False):
        return self._links.link(for_entity=self._instance, to_entity=value, main=main)

    add = append

    def remove(self, value):
        return self._links.unlink(for_entity=self._instance, to_entity=value)


class _EmbeddedLinkField(_Link):
    _path = [
        "_embedded",
    ]

    def on_get(self, data):
        if data:
            return self._model.objects.get(data[0]["id"])
        return None

    def on_set_instance(self, instance, value):
        if instance.id is None:
            raise exceptions.InitException("Create entity first")
        if value.id is None:
            value.create()
        self._links.link(instance, value)
        return [{"id": value.id}]


class _EmbeddedLinkListField(_Link):
    _path = [
        "_embedded",
    ]

    def on_get_instance(self, instance, value):
        return _ListData(data=value, model=self._model, manager=self._manager, instance=instance, links=self._links)

    def on_set(self, value):
        raise TypeError()
