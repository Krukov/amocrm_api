from . import fields, manager, model
from .interaction import BaseInteraction


class AccountInteraction(BaseInteraction):
    def get(self, object_id=None, include=None):
        response, _ = self.request("get", "account", include=include)
        return response


class Account(model.Model):
    name = fields._Field("name")
    subdomain = fields._Field("subdomain")
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    current_user = fields._Link("current_user_id", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    country = fields._Field("country")
    customers_mode = fields._Field("customers_mode")
    is_unsorted_on = fields._Field("is_unsorted_on")
    is_loss_reason_enabled = fields._Field("is_loss_reason_enabled")
    is_helpbot_enabled = fields._Field("is_helpbot_enabled")
    is_technical_account = fields._Field("is_technical_account")
    contact_name_display_order = fields._Field("contact_name_display_order")
    version = fields._Field("version", is_embedded=True)

    users_groups = fields._Field("users_groups", path=["_embedded"])
    task_types = fields._Field("task_types", path=["_embedded"])
    datetime_settings = fields._Field("datetime_settings", path=["_embedded"])
    entity_names = fields._Field("entity_names", path=["_embedded"])


def get_account_info(*args, **kwargs):
    return manager.Manager(AccountInteraction(*args, **kwargs), model=Account).get()
