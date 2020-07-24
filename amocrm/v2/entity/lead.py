
from ..interaction import GenericInteraction
from .. import fields, model, manager


class _StatusesField(fields._BaseField):
    _path = []

    def __init__(self):
        super().__init__("status_id", blank=True)

    def on_get_instance(self, instance, status_id):
        for status in instance.pipeline.statuses:
            if status.id == status_id:
                return status


class LeadsInteraction(GenericInteraction):
    path = "leads"


class Lead(model.Model):
    name = fields._Field("name")
    responsible_user = fields._Link("responsible_user_id", "User")
    group = fields._UnEditableField("group_id")
    price = fields._Field("price")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    closest_task_at = fields._DateTimeField("closest_task_at", blank=True)
    account_id = fields._UnEditableField("account_id")
    is_deleted = fields._UnEditableField("is_deleted")
    score = fields._UnEditableField("score", blank=True)

    loss_reason_id = fields._Field("loss_reason_id", blank=True)
    status = _StatusesField()
    pipeline = fields._Link("pipeline_id", "Pipeline")

    # loss_reason = fields._Field("name", path=["_embedded", "loss_reason"])
    contacts = fields._EmbeddedLinkListField("contacts", model="Contact")

    tags = fields._TagsField()

    # catalog_elements = fields._EmbeddedLinkListField("catalog_elements", Customer)

    objects = manager.Manager(LeadsInteraction())
