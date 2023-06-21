from datetime import datetime

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
EVENT_TYPE_TASK_TEXT_CHANGE = "task_text_changed"
EVENT_TYPE_ROBOT_REPLIED = "robot_replied"
EVENT_TYPE_INTENT_IDENTIFIED = "intent_identified"
EVENT_TYPE_TRANSACTION_ADDED = "transaction_added"
EVENT_TYPE_NPS_RATE_ADDED = "nps_rate_added"
EVENT_TYPE_INCOMING_CHAT_MESSAGE = "incoming_chat_message"
EVENT_TYPE_OUTGOING_CHAT_MESSAGE = "outgoing_chat_message"
EVENT_TYPE_ENTITY_TAG_ADDED = "entity_tag_added"
EVENT_TYPE_ENTITY_TAG_DELETED = "entity_tag_deleted"
EVENT_TYPE_CUSTOMER_STATUS_CHANGED = "customer_status_changed"
EVENT_TYPE_ENTITY_RESPONSIBLE_CHANGED = "entity_responsible_changed"
EVENT_TYPE_TASK_DEADLINE_CHANGED = "task_deadline_changed"
EVENT_TYPE_CUSTOM_FIELD_VALUE_CHANGED = "custom_field_value_changed"
EVENT_TYPE_TASK_TYPE_CHANGED = "task_type_changed"
EVENT_TYPES_WITH_NOTE = (
    "lead_added",
    "contact_added",
    "company_added",
    "customer_added",
    "common_note_added",
    "common_note_deleted",
    "attachment_note_added",
    "targeting_in_note_added",
    "targeting_out_note_added",
    "geo_note_added",
    "service_note_added",
    "site_visit_note_added",
    "message_to_cashier_note_added",
    "incoming_call",
    "outgoing_call",
    "incoming_sms",
    "outgoing_sms",
    "link_followed",
    "task_result_added",
)
EVENT_TYPES_LINK_ENTITY = (
    "customer_linked",
    "customer_unlinked",
    "company_linked",
    "company_unlinked",
    "contact_linked",
    "contact_unlinked",
    "lead_linked",
    "lead_unlinked",
    "entity_linked",
    "entity_unlinked",
)
EVENT_REQUEST_LIMIT = 100


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
            return value[0]["lead_status"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_TASK_TEXT_CHANGE:
            return value[0]["task"]["text"] if len(value) != 0 else None
        if instance.type in [EVENT_TYPE_INTENT_IDENTIFIED, EVENT_TYPE_ROBOT_REPLIED]:
            return value[0]["helpbot"]["id"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_TRANSACTION_ADDED:
            return value[0]["transaction"]["id"] if len(value) != 0 else None
        if instance.type in EVENT_TYPES_WITH_NOTE:
            return value[0]["note"]["id"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_NPS_RATE_ADDED:
            return value[0]["nps"]["rate"] if len(value) != 0 else None
        if instance.type in [EVENT_TYPE_INCOMING_CHAT_MESSAGE, EVENT_TYPE_OUTGOING_CHAT_MESSAGE]:
            return value[0]["message"]["id"] if len(value) != 0 else None
        if instance.type in [EVENT_TYPE_ENTITY_TAG_DELETED, EVENT_TYPE_ENTITY_TAG_ADDED]:
            return [item["tag"]["name"] for item in value]
        if instance.type == EVENT_TYPE_CUSTOMER_STATUS_CHANGED:
            return value[0]["customer_status"]["id"] if len(value) != 0 else None
        if instance.type in EVENT_TYPES_LINK_ENTITY:
            return value[0]["link"]["entity"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_ENTITY_RESPONSIBLE_CHANGED:
            return value[0]["responsible_user"]["id"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_TASK_TYPE_CHANGED:
            return value[0]["task_type"]["id"] if len(value) != 0 else None
        if instance.type == EVENT_TYPE_CUSTOM_FIELD_VALUE_CHANGED:
            return [item["custom_field_value"] for item in value]
        if instance.type == EVENT_TYPE_TASK_DEADLINE_CHANGED:
            return datetime.utcfromtimestamp(float(value[0]["task_deadline"]["timestamp"]))
        return value


class EventsInteraction(GenericInteraction):
    path = "events"

    def get_all(self, include=None, query=None, filters=(), order=None):
        for data in self._all(self._get_path(), include=include, query=query, filters=filters, order=order, limit=EVENT_REQUEST_LIMIT):
            yield from data[self._get_field()]

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
