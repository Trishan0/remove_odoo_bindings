from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        blacklist = list(super()._load_menus_blacklist())
        hide_stores = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("remove_odoo_bindings.hide_app_store", "True")
            .lower()
            == "true"
        )
        if hide_stores:
            for xmlid in ("base.menu_third_party", "base.menu_theme_store"):
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu:
                    blacklist.append(menu.id)
        return list(dict.fromkeys(blacklist))
