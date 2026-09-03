{
    "name": "Complete White Label Branding",
    "summary": "Replace visible vendor branding and configure a branded backend URL",
    "description": """
Complete white-label branding for Odoo 17.0.

Configure the product name, browser/PWA identity, colors, favicon, support
links, login and email footers, backend URL slug, app-store links, and optional
systray visibility from General Settings.
    """,
    "version": "17.0.2.0.0",
    "author": "Trishan Fernando",
    "website": "https://trishanfernando.com",
    "license": "LGPL-3",
    "category": "Tools",
    "depends": ["base_setup", "web", "mail", "base_import"],
    "data": [
        "views/ir_ui_menu.xml",
        "views/res_config_settings_views.xml",
        "views/webclient_templates.xml",
        "views/mail_templates.xml",
    ],
    "images": ["static/description/banner.png"],
    "assets": {
        "web.assets_backend": [
            "remove_odoo_bindings/static/src/js/white_label.js",
            "remove_odoo_bindings/static/src/scss/white_label.scss",
            "remove_odoo_bindings/static/src/xml/error_dialogs.xml",
            "remove_odoo_bindings/static/src/import_action/import_action_inherit.xml",
            "remove_odoo_bindings/static/src/import_data_content/import_data_content_inherit.xml",
            "remove_odoo_bindings/static/src/import_data_sidepanel/import_data_sidepanel_inherit.xml",
        ],
        "web.assets_frontend": [
            "remove_odoo_bindings/static/src/scss/white_label.scss",
            "remove_odoo_bindings/static/src/xml/error_dialogs.xml",
        ],
    },
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
