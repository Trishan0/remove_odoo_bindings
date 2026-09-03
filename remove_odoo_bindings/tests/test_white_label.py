from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWhiteLabelBranding(TransactionCase):
    def test_install_defaults_are_applied(self):
        parameters = self.env["ir.config_parameter"].sudo()

        self.assertEqual(
            parameters.get_param("remove_odoo_bindings.backend_slug"), "erp"
        )
        self.assertEqual(
            parameters.get_param("remove_odoo_bindings.hide_app_store"), "True"
        )
        self.assertEqual(self.env.ref("base.partner_root").name, "Assistant")

    def test_company_branding_values(self):
        company = self.env["res.company"].create(
            {
                "name": "Example Company",
                "white_label_brand_name": "Example Suite",
                "white_label_primary_color": "#123ABC",
                "white_label_support_url": "https://support.example.com",
            }
        )

        values = company._white_label_values()

        self.assertEqual(values["brand_name"], "Example Suite")
        self.assertEqual(values["primary_color"], "#123ABC")
        self.assertEqual(values["support_url"], "https://support.example.com")

    def test_rejects_invalid_color(self):
        with self.assertRaises(ValidationError):
            self.env["res.company"].create(
                {
                    "name": "Invalid Color",
                    "white_label_primary_color": "blue",
                }
            )

    def test_rejects_unsafe_or_incomplete_urls(self):
        for url in ("javascript:alert(1)", "/relative", "example.com"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                self.env["res.company"].create(
                    {
                        "name": "Invalid URL",
                        "white_label_support_url": url,
                    }
                )

    def test_backend_slug_validation(self):
        settings_model = self.env["res.config.settings"]
        for slug in ("Odoo", "a", "shop", "bad_slug", " bad"):
            with self.subTest(slug=slug), self.assertRaises(ValidationError):
                settings_model.create({"white_label_backend_slug": slug})

        settings = settings_model.create({"white_label_backend_slug": "company-erp"})
        self.assertEqual(settings.white_label_backend_slug, "company-erp")

    def test_vendor_store_menus_are_blacklisted(self):
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param("remove_odoo_bindings.hide_app_store", "True")

        blacklist = self.env["ir.ui.menu"]._load_menus_blacklist()

        self.assertIn(self.env.ref("base.menu_third_party").id, blacklist)
        self.assertIn(self.env.ref("base.menu_theme_store").id, blacklist)
