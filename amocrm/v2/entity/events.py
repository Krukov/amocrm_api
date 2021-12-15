from ... import fields, manager, model
from ..interaction import GenericInteraction
from .note import NotesField
from .pipeline import Status
from .tag import TagsField


class EventsInteraction(GenericInteraction):
    path = "events"


class Event(model.Model):
    type = fields._Field("type")
    entity_id = fields._UnEditableField("entity_id")
    entity_type = fields._Field("note_type")
    created_by = fields._Link("created_by", "User")
    created_at = fields._DateTimeField("created_at")
    account_id = fields._UnEditableField("account_id")
    value_after = fields._Field("value_after", path=["value_after"])
    value_before = fields._Field("value_before", path=["value_before"])
    


    objects = manager.Manager(EventsInteraction())
