import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


BACKEND_SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
RESERVED_SLUGS = {
    "api",
    "blog",
    "contactus",
    "event",
    "forum",
    "jobs",
    "livechat",
    "mail",
    "my",
    "odoo",
    "payment",
    "pos",
    "report",
    "shop",
    "slides",
    "static",
    "web",
    "websocket",
    "website",
}


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    white_label_brand_name = fields.Char(
        related="company_id.white_label_brand_name",
        readonly=False,
    )
    white_label_website_url = fields.Char(
        related="company_id.white_label_website_url",
        readonly=False,
    )
    white_label_support_url = fields.Char(
        related="company_id.white_label_support_url",
        readonly=False,
    )
    white_label_documentation_url = fields.Char(
        related="company_id.white_label_documentation_url",
        readonly=False,
    )
    white_label_favicon = fields.Binary(
        related="company_id.white_label_favicon",
        readonly=False,
    )
    white_label_primary_color = fields.Char(
        related="company_id.white_label_primary_color",
        readonly=False,
    )
    white_label_login_footer = fields.Char(
        related="company_id.white_label_login_footer",
        readonly=False,
    )
    white_label_email_footer = fields.Char(
        related="company_id.white_label_email_footer",
        readonly=False,
    )
    white_label_show_help = fields.Boolean(
        related="company_id.white_label_show_help",
        readonly=False,
    )
    white_label_hide_messaging = fields.Boolean(
        related="company_id.white_label_hide_messaging",
        readonly=False,
    )
    white_label_hide_activities = fields.Boolean(
        related="company_id.white_label_hide_activities",
        readonly=False,
    )
    white_label_backend_slug = fields.Char(
        string="Backend URL Slug",
        config_parameter="remove_odoo_bindings.backend_slug",
        default="erp",
        help="Replaces /web as the backend entry URL, for example /erp.",
    )
    white_label_hide_app_store = fields.Boolean(
        string="Hide Vendor App Stores",
        config_parameter="remove_odoo_bindings.hide_app_store",
        default=True,
        help="Hide Third-Party Apps and Theme Store while retaining installed-app management.",
    )
    white_label_assistant_name = fields.Char(
        string="Assistant Name",
        config_parameter="remove_odoo_bindings.assistant_name",
        default="Assistant",
        help="Display name of the built-in automated assistant.",
    )

    @api.constrains("white_label_backend_slug")
    def _check_white_label_backend_slug(self):
        for settings in self:
            raw_slug = settings.white_label_backend_slug or ""
            slug = raw_slug.strip()
            if raw_slug != slug or not BACKEND_SLUG_RE.fullmatch(slug):
                raise ValidationError(
                    _(
                        "Backend URL slug must be 2-40 lowercase letters, numbers, or hyphens, "
                        "and must start with a letter."
                    )
                )
            if slug in RESERVED_SLUGS:
                raise ValidationError(_("The backend URL slug '%s' is reserved.", slug))

    def set_values(self):
        result = super().set_values()
        brand_name = self.company_id.white_label_brand_name or self.company_id.name
        self.env["ir.config_parameter"].sudo().set_param("web.web_app_name", brand_name)
        assistant = self.env.ref("base.partner_root", raise_if_not_found=False)
        if assistant:
            assistant.sudo().name = self.white_label_assistant_name or "Assistant"
        self.env.registry.clear_cache()
        return result
