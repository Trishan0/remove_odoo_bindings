from . import controllers
from . import models


def post_init_hook(env):
    parameters = env["ir.config_parameter"].sudo()
    defaults = {
        "remove_odoo_bindings.backend_slug": "erp",
        "remove_odoo_bindings.hide_app_store": "True",
        "remove_odoo_bindings.assistant_name": "Assistant",
    }
    for key, value in defaults.items():
        if not parameters.search_count([("key", "=", key)]):
            parameters.set_param(key, value)

    company = env.company.sudo()
    brand_name = company.white_label_brand_name or company.name
    parameters.set_param("web.web_app_name", brand_name)
    assistant = env.ref("base.partner_root", raise_if_not_found=False)
    if assistant and assistant.name == "OdooBot":
        assistant.name = parameters.get_param(
            "remove_odoo_bindings.assistant_name", "Assistant"
        )


def uninstall_hook(env):
    parameters = env["ir.config_parameter"].sudo()
    assistant_name = parameters.get_param(
        "remove_odoo_bindings.assistant_name", "Assistant"
    )
    assistant = env.ref("base.partner_root", raise_if_not_found=False)
    if assistant and assistant.name == assistant_name:
        assistant.name = "OdooBot"
    parameters.set_param("web.web_app_name", "Odoo")
    module_parameters = parameters.search([]).filtered(
        lambda parameter: parameter.key.startswith("remove_odoo_bindings.")
    )
    module_parameters.unlink()
    env.registry.clear_cache()
