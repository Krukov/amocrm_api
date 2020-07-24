from ..interaction import GenericInteraction
from .. import fields, model, manager


class LeadsTagsInteraction(GenericInteraction):
    path = "leads/tags"


class ContactsTagsInteraction(GenericInteraction):
    path = "contacts/tags"


class CompaniesTagsInteraction(GenericInteraction):
    path = "companies/tags"


class CustomersTagsInteraction(GenericInteraction):
    path = "customers/tags"


class Tag(model.Model):
    name = fields._Field()

    leads = manager.Manager(LeadsTagsInteraction())
    contacts = manager.Manager(ContactsTagsInteraction())
    companies = manager.Manager(CompaniesTagsInteraction())
    customers = manager.Manager(CustomersTagsInteraction())
