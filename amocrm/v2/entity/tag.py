from .. import fields, manager, model
from ..interaction import GenericInteraction


class Tag(model.Model):
    name = fields._Field("name")

    leads = manager.Manager(GenericInteraction(path="leads/tags"))
    contacts = manager.Manager(GenericInteraction(path="contacts/tags"))
    companies = manager.Manager(GenericInteraction(path="companies/tags"))
    customers = manager.Manager(GenericInteraction(path="customers/tags"))


class _TagsList:
    def __init__(self, tags, on_change):
        """
        BAD CODE THERE
        self._tags is mutable object and this class and arch play with it
        """
        self._tags = tags
        self._on_change = on_change

    def __iter__(self):
        yield from (Tag(data=item) for item in self._tags)

    def _add(self, tag):
        self._tags.append(tag)
        self._on_change()

    def append(self, value):
        if isinstance(value, Tag):
            if value.id is None:
                value.create()
            self._add({"id": value.id})
        else:
            self._add({"name": value})

    add = append

    def remove(self, value):
        if isinstance(value, Tag):
            value = value.id
        self._remove(value)

    def _remove(self, value):
        for tag in self._tags:
            if tag["id"] == value or tag["name"] == value:
                self._tags.remove(tag)
                self._on_change()
                return


class TagsField(fields._BaseField):
    _path = ["_embedded"]

    def __init__(self):
        super().__init__("tags", blank=True)

    def on_get_instance(self, instance, tags):
        if tags is None:
            tags = instance._data.setdefault("_embedded", {}).setdefault("tags", [])
        return _TagsList(tags, on_change=lambda: self._notify_instance(instance))
