from .. import fields, manager, model
from ..interaction import GenericInteraction

COMMON_TYPE = "common"  # Обычное примечание
CALL_IN_TYPE = "call_in"  # Входящий звонок
CALL_OUT_TYPE = "call_out"  # Исходящий звонок
SERVICE_MESSAGE_TYPE = "service_message"  # Системное сообщение
CASHIER_MESSAGE_TYPE = "message_cashier"  # Сообщение кассиру
INVOICE_PAID_TYPE = "invoice_paid"  # Оплата счета
GEOLOCATION_TYPE = "geolocation"  # Геолокация
SMS_IN_TYPE = "sms_in"  # Входящее сообщение
SMS_OUT_TYPE = "sms_out"  # Исходящее сообщение
# "extended_service_message	Системное примечание


class NotesInteraction(GenericInteraction):
    path = "{entity_type}/{entity_id}/notes"


class NotesField(fields._UnEditableField):
    def __init__(self):
        super().__init__(blank=True, is_embedded=False)

    def on_get_instance(self, instance, value):
        class Note(_Note):
            objects = manager.Manager(NotesInteraction(path=f"{instance._path}/{instance.id}/notes", field="notes"))

        return Note


class _AutoTypeField(fields._Field):
    def __init__(self, *args, note_type, **kwargs):
        self._auto_type = note_type
        super().__init__(*args, blank=True, path=["params"], **kwargs)

    def on_set_instance(self, instance, value):
        instance._data["note_type"] = self._auto_type
        return super().on_set_instance(instance, value)


class _Note(model.Model):
    note_type = fields._Field("note_type")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    responsible_user = fields._Link("responsible_user_id", "User")

    objects = manager.Manager(NotesInteraction())

    # Type fields

    text = _AutoTypeField("text", note_type=COMMON_TYPE)

    uniq = _AutoTypeField("uniq", note_type=CALL_IN_TYPE)
    duration = _AutoTypeField("duration", note_type=CALL_IN_TYPE)
    source = _AutoTypeField("source", note_type=CALL_IN_TYPE)
    link = _AutoTypeField("link", note_type=CALL_IN_TYPE)
    phone = _AutoTypeField("phone", note_type=CALL_IN_TYPE)

    address = _AutoTypeField("address", note_type=GEOLOCATION_TYPE)
    longitude = _AutoTypeField("longitude", note_type=GEOLOCATION_TYPE)
    latitude = _AutoTypeField("latitude", note_type=GEOLOCATION_TYPE)
