from .. import fields, manager, model
from ..interaction import GenericInteraction


EVENT_TYPES_WITH_BLANK_VALUE = (
    "lead_deleted",
    "lead_restored",
    "contact_deleted",
    "contact_restored",
    "company_deleted",
    "company_restored",
    "customer_deleted",
    "entity_merged",
    "task_added",
    "task_deleted",
    "task_completed",
)
EVENT_TYPE_LEAD_STATUS_CHANGE = "lead_status_changed"


class _EventValueField(fields._UnEditableField):
    def on_get_instance(self, instance, value):
        """
        value here is what we have in value_after/value_before field
        For example
        [
            {
                "note": {
                    "id": 42743871
                }
            }
        ],
        """
        if instance.type in EVENT_TYPES_WITH_BLANK_VALUE:
            return None
        if instance.type == EVENT_TYPE_LEAD_STATUS_CHANGE:
            return value[0]["lead_status"]


class Event:
    value_after = _EventValueField("value_after")
    value_before = _EventValueField("value_before")


class EventsInteraction(GenericInteraction):
    path = "events"


class Event(model.Model):
    type = fields._Field("type")
    entity_id = fields._UnEditableField("entity_id")
    entity_type = fields._UnEditableField("entity_type")
    created_by = fields._Link("created_by", "User")
    created_at = fields._DateTimeField("created_at")
    account_id = fields._UnEditableField("account_id")
    value_after = _EventValueField("value_after")
    value_before = _EventValueField("value_before")

    objects = manager.Manager(EventsInteraction())
