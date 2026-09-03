import re
from urllib.parse import urlparse

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class ResCompany(models.Model):
    _inherit = "res.company"

    white_label_brand_name = fields.Char(
        string="Product Name",
        default="Business Suite",
        help="Name shown in browser titles, dialogs, the PWA, and branded footers.",
    )
    white_label_website_url = fields.Char(
        string="Brand Website",
        help="Public website opened from branded footer links.",
    )
    white_label_support_url = fields.Char(
        string="Support URL",
        help="Optional helpdesk URL used by the Help user-menu item.",
    )
    white_label_documentation_url = fields.Char(
        string="Documentation URL",
        help="Optional documentation URL used instead of vendor documentation.",
    )
    white_label_favicon = fields.Binary(
        string="Favicon / PWA Icon",
        attachment=True,
        help="Square PNG or ICO image used for browser tabs and the installed web app.",
    )
    white_label_primary_color = fields.Char(
        string="Interface Primary Color",
        default="#2563EB",
        help="Six-digit hexadecimal color used for the backend navigation and primary actions.",
    )
    white_label_login_footer = fields.Char(
        string="Login Footer",
        help="Optional text displayed below login, sign-up, and password-reset forms.",
    )
    white_label_email_footer = fields.Char(
        string="Email Footer",
        help="Optional product credit displayed in notification emails.",
    )
    white_label_show_help = fields.Boolean(
        string="Show Help Link",
        default=False,
        help="Show the Help item when a custom support URL is configured.",
    )
    white_label_hide_messaging = fields.Boolean(
        string="Hide Messages Menu",
        default=True,
        help="Hide the messaging systray menu. This changes functionality, not only branding.",
    )
    white_label_hide_activities = fields.Boolean(
        string="Hide Activities Menu",
        default=True,
        help="Hide the activities systray menu. This changes functionality, not only branding.",
    )

    @api.constrains("white_label_primary_color")
    def _check_white_label_primary_color(self):
        for company in self:
            if company.white_label_primary_color and not HEX_COLOR_RE.fullmatch(
                company.white_label_primary_color
            ):
                raise ValidationError(_("Primary color must use the #RRGGBB format."))

    @api.constrains(
        "white_label_website_url",
        "white_label_support_url",
        "white_label_documentation_url",
    )
    def _check_white_label_urls(self):
        field_names = (
            "white_label_website_url",
            "white_label_support_url",
            "white_label_documentation_url",
        )
        for company in self:
            for field_name in field_names:
                value = company[field_name]
                if not value:
                    continue
                parsed = urlparse(value)
                if parsed.scheme not in ("http", "https") or not parsed.netloc:
                    raise ValidationError(
                        _("Brand, support, and documentation URLs must be complete HTTP(S) URLs.")
                    )

    def _white_label_values(self):
        self.ensure_one()
        return {
            "brand_name": self.white_label_brand_name or self.name,
            "website_url": self.white_label_website_url or self.website or "",
            "support_url": self.white_label_support_url or "",
            "documentation_url": self.white_label_documentation_url or "",
            "primary_color": self.white_label_primary_color or "#2563EB",
            "login_footer": self.white_label_login_footer or "",
            "email_footer": self.white_label_email_footer or "",
            "show_help": self.white_label_show_help,
            "hide_messaging": self.white_label_hide_messaging,
            "hide_activities": self.white_label_hide_activities,
            "has_favicon": bool(self.white_label_favicon),
        }
