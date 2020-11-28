from .. import fields, manager, model
from ..interaction import GenericInteraction
from .note import NotesField
from .tag import TagsField


class ContactsInteraction(GenericInteraction):
    path = "contacts"


class Contact(model.Model):

    name = fields._Field("name")
    first_name = fields._Field("first_name", blank=True)
    last_name = fields._Field("last_name", blank=True)
    responsible_user = fields._Link("responsible_user_id", "User")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    closest_task_at = fields._DateTimeField("closest_task_at", blank=True)
    account_id = fields._UnEditableField("account_id")
    tags = TagsField()

    company = fields._EmbeddedLinkField("companies", "Company")
    leads = fields._EmbeddedLinkListField("leads", "Lead")

    notes = NotesField()

    objects = manager.Manager(ContactsInteraction())
