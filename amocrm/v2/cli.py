import os
from typing import Iterable, Type

from slugify import slugify as _slugify

from . import tokens
from .entity import company, contact, custom_field, lead
from .interaction import GenericInteraction
from .manager import Manager
from .model import Model

getenv = os.getenv

CUSTOM_FIELDS_PKG = "custom_field"
INIT_TEMPLATE = """
from amocrm.v2 import tokens, custom_field


tokens.default_token_manager(
    client_secret="{secret}",
    client_id="{client_id}",
    subdomain="{subdomain}",
    redirect_url="{redirect_url}",
    storage=tokens.FileTokensStorage(directory_path="{path}"),
)
# code = ...
# if code:
#     tokens.default_token_manager.init(code, skip_error=True)
"""
MODELS = [contact.Contact, company.Company, lead.Lead]
SLUGIFY_SEP = "_"
SLUGIFY_REPLACE = (
    ("1", "one"),
    ("2", "two"),
    ("3", "three"),
    ("4", "four"),
    ("5", "five"),
    ("6", "six"),
    ("7", "seven"),
    ("8", "eight"),
    ("9", "nine"),
    ("0", "zero"),
)


def slugify(text):
    return _slugify(text, separator=SLUGIFY_SEP, replacements=SLUGIFY_REPLACE)


def render_models_file(init_token, enums=True):
    out = ""
    for model in MODELS:
        out += f"\nfrom amocrm.v2 import {model.__name__} as _{model.__name__}"
    out += init_token
    for model in MODELS:
        out += "\n\n"
        out += render_model(model, enums)
    return out


def render_model(model: Type[Model], enums=True):
    out = f"\nclass {model.__name__}(_{model.__name__}):"
    for field in get_fields_for(model):
        out += "\n" + render_field(field, enums=enums)
    return out


def get_fields_for(model: Type[Model]) -> Iterable[custom_field.CustomFieldModel]:
    return Manager(
        GenericInteraction(path=f"{model.objects._interaction.path}/custom_fields", field="custom_fields",),
        model=custom_field.CustomFieldModel,
    ).all()


def render_field(field: custom_field.CustomFieldModel, enums=True) -> str:
    field_name = slugify(field.name)
    field_type = _get_field_type(field)
    out = ""
    enums = (
        enums
        and field.type in (custom_field.MULTISELECT, custom_field.RADIOBUTTON, custom_field.SELECT)
        and field.enums
    )
    if enums:
        out += render_field_enums(field)
        out += "\n"
    out += f'    {field_name} = {CUSTOM_FIELDS_PKG}.{field_type}("{field.name}", field_id={field.id}'
    if field.code:
        out += f', code="{field.code}"'
    if enums:
        out += f", enums={field_name.upper()}_ENUMS"
    return out + ")"


def render_field_enums(field: custom_field.CustomFieldModel) -> str:
    field_name = slugify(field.name)
    out = f"\n    class {field_name.upper()}_ENUMS:"
    for enum in field.enums:
        enum_name = slugify("_".join(enum["value"].split(" ")[:3]))
        out += f"\n        {enum_name} = {CUSTOM_FIELDS_PKG}.SelectValue(id={enum['id']}, value='{enum['value']}')"
    return out


def _get_field_type(field: custom_field.CustomFieldModel) -> str:
    return custom_field._get_field_class(field.type, field.code)


def main():
    client_id, secret, subdomain, redirect_url, path, code, enums = get_args()
    gen(client_id, secret, subdomain, redirect_url, path, code, enums)


def get_args():
    check_envs()
    return (
        getenv("AMOCRM_CLIENT_ID"),
        getenv("AMOCRM_SECRET"),
        getenv("AMOCRM_SUBDOMAIN"),
        getenv("AMOCRM_REDIRECT_URL"),
        getenv("AMOCRM_TOKEN_STORE_PATH", os.getcwd()),
        getenv("AMOCRM_CODE"),
        not bool(getenv("AMOCRM_DO_NOT_GEN_ENUMS")),
    )


def check_envs():
    for env in ("AMOCRM_CLIENT_ID", "AMOCRM_SECRET", "AMOCRM_SUBDOMAIN", "AMOCRM_REDIRECT_URL"):
        if not getenv(env):
            raise EnvironmentError(f"Set {env} environment value `export {env}='value form amocrm settings'`")


def gen(client_id, secret, subdomain, redirect_url, path, code=None, enums=True):
    tokens.default_token_manager(
        client_secret=secret,
        client_id=client_id,
        subdomain=subdomain,
        redirect_url=redirect_url,
        storage=tokens.FileTokensStorage(directory_path=path),
    )
    if code:
        tokens.default_token_manager.init(code, skip_error=True)
    init_token = INIT_TEMPLATE.format(
        secret=secret, client_id=client_id, subdomain=subdomain, redirect_url=redirect_url, path=path
    )
    try:
        print(render_models_file(init_token, enums))
    except:
        raise EnvironmentError(
            "Set AMOCRM_CODE environment value from amocrm settings or check other environment values with prefix AMOCRM"
        )


if __name__ == "__main__":
    main()
