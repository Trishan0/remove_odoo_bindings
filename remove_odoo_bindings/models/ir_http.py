from odoo import models
from odoo.http import request


DEFAULT_BACKEND_SLUG = "erp"


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _white_label_backend_slug(cls):
        if not request.db:
            return DEFAULT_BACKEND_SLUG
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("remove_odoo_bindings.backend_slug", DEFAULT_BACKEND_SLUG)
        )

    @classmethod
    def _match(cls, path_info):
        """Map the configured branded entry point to Odoo 17's /web route."""
        slug = cls._white_label_backend_slug()
        if path_info == f"/{slug}":
            path_info = "/web"
        return super()._match(path_info)

    def session_info(self):
        result = super().session_info()
        company = self.env.company.sudo()
        white_label = company._white_label_values()
        white_label["backend_slug"] = self._white_label_backend_slug()
        white_label["hide_app_store"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("remove_odoo_bindings.hide_app_store", "True")
            .lower()
            == "true"
        )
        result["white_label"] = white_label
        if white_label["show_help"] and white_label["support_url"]:
            result["support_url"] = white_label["support_url"]
        else:
            result["support_url"] = ""
        return result
