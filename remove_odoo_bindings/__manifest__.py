{
    "name": "Remove Odoo Bindings",
    "description": "This module removes the odoo.com bindings and systray icons from the user menu.",
    "version": "19.0.1.0.0",
    "author": "Trishan Fernando",
    "license": "LGPL-3",
    "category": "Tools",
    "depends": ["base","auth_totp","mail",'mail_bot','base_import','auth_signup'],
    "data": [
        "views/ir_ui_menu.xml",
        "views/preferences_form.xml",
        "views/res_config_settings_views.xml"
        "views/webclient_templates.xml",
        ],
    "images": ['static/description/banner.png'],
    "assets": {
        "web.assets_backend": [
            "remove_odoo_bindings/static/src/js/user_menu_items.esm.js",
            "remove_odoo_bindings/static/src/import_action/import_action_inherit.xml",
            "remove_odoo_bindings/static/src/import_data_content/import_data_content_inherit.xml",
            "remove_odoo_bindings/static/src/import_data_sidepanel/import_data_sidepanel_inherit.xml",
        ],
    },
    "installable": True,
}
