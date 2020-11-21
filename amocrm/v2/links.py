from . import exceptions
from .interaction import BaseInteraction


class LinksInteraction(BaseInteraction):
    def link(self, for_entity, to_entity, main=False, metadata=None):
        return self._set("link", for_entity, to_entity, main=main, metadata=metadata)

    def unlink(self, for_entity, to_entity):
        return self._set("link", for_entity, to_entity)

    def _set(self, direction, for_entity, to_entity, main=False, metadata=None):
        path = "{}/{}/{}".format(for_entity._path, for_entity.id, direction)
        data = {"to_entity_id": to_entity.id, "to_entity_type": to_entity._path}
        if main:
            metadata = metadata or {}
            metadata["main"] = True
        data["metadata"] = metadata
        response, status = self.request("post", path, data=[data])
        if status == 400:
            raise exceptions.ValidationError(response)
