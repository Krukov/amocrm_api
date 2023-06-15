from .. import fields, manager, model
from ..interaction import GenericInteraction
from .note import NotesField
from .tag import TagsField
from .task import TaskField
from amocrm.v2 import custom_field


class ListsInteraction(GenericInteraction):
    path = "catalogs"


class List(model.Model):

    name = fields._Field("name")
    type = fields._Field("type", blank=True)
    sort = fields._Field("sort")
    can_add_elements = fields._Field("can_add_elements")
    can_link_multiple = fields._Field("can_link_multiple")
    tags = TagsField()

    company = fields._EmbeddedLinkField("companies", "Company")
    leads = fields._EmbeddedLinkListField("leads", "Lead")

    notes = NotesField()
    tasks = TaskField("catalogs")

    objects = manager.Manager(ListsInteraction())

# Implemented a class for lists
# amocrm api - https://www.amocrm.ru/developers/content/crm_platform/catalogs-api#lists-add
