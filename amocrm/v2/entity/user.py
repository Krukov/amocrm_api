from .. import fields, manager, model
from ..interaction import GenericInteraction


class UsersInteraction(GenericInteraction):
    path = "users"


class User(model.Model):
    name = fields._Field("name")
    email = fields._Field("email")
    language = fields._Field("lang")
    mail_access = fields._Field("mail_access", path=["rights"])
    catalog_access = fields._Field("catalog_access", path=["rights"])
    status_rights = fields._Field("status_rights", path=["rights"], blank=True)
    is_admin = fields._Field("is_admin", path=["rights"])
    is_free = fields._Field("is_free", path=["rights"])
    is_active = fields._Field("is_active", path=["rights"])

    objects = manager.Manager(interaction=UsersInteraction())
