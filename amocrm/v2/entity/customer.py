from .. import fields, manager, model
from ..interaction import GenericInteraction
from .tag import TagsField


class CustomersInteraction(GenericInteraction):
    path = "customers"

    def enable(self, mode: str = "segments"):
        return self.set(True, mode=mode)

    def disable(self):
        return self.set(False)

    def set(self, enable: bool, mode: str = "segments"):
        data, _ = self.request("patch", path="customers/mode", data={"is_enabled": enable, "mode": mode})
        return data


class Customer(model.Model):

    name = fields._Field("name")
    next_price = fields._Field("next_price")
    next_date = fields._DateTimeField("next_date")
    responsible_user = fields._Link("responsible_user_id", "User")
    periodicity = fields._Field("periodicity")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    closest_task_at = fields._DateTimeField("closest_task_at", blank=True)
    is_deleted = fields._Field("is_deleted")
    ltv = fields._Field("ltv")
    purchases_count = fields._Field("purchases_count")
    average_check = fields._Field("average_check")

    account_id = fields._UnEditableField("account_id")
    tags = TagsField()

    contacts = fields._EmbeddedLinkListField("contacts", "Contact")
    company = fields._EmbeddedLinkField("companies", "Company")

    objects = manager.Manager(CustomersInteraction())
