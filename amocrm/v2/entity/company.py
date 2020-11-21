from .. import fields, manager, model
from ..interaction import GenericInteraction
from .note import NotesField
from .tag import TagsField


class CompaniesInteraction(GenericInteraction):
    path = "companies"


class Company(model.Model):
    name = fields._Field("name")
    responsible_user = fields._Link("responsible_user_id", "User")
    group = fields._Field("group_id")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    closest_task_at = fields._DateTimeField("closest_task_at", blank=True)
    account_id = fields._UnEditableField("account_id")

    tags = TagsField()
    notes = NotesField()

    leads = fields._EmbeddedLinkListField("leads", "Lead")
    customers = fields._EmbeddedLinkListField("customers", "Customer")
    contacts = fields._EmbeddedLinkListField("contacts", "Contact")

    objects = manager.Manager(CompaniesInteraction())
