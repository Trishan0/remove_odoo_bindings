import json
from urllib.parse import urlsplit, urlunsplit

from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.webmanifest import WebManifest
from odoo.http import request


class WhiteLabelHome(Home):
    @staticmethod
    def _replace_backend_prefix(location):
        if not location or not request.db:
            return location
        slug = request.env["ir.http"]._white_label_backend_slug()
        parsed = urlsplit(location)
        path = parsed.path
        if path == "/odoo" or path.startswith("/odoo/"):
            path = f"/{slug}{path[5:]}"
        return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    @http.route()
    def index(self, s_action=None, db=None, **kw):
        response = super().index(s_action=s_action, db=db, **kw)
        if response.status_code in (301, 302, 303, 307, 308):
            response.headers["Location"] = self._replace_backend_prefix(
                response.headers.get("Location")
            )
        return response

    @http.route()
    def web_client(self, s_action=None, **kw):
        path = request.httprequest.path
        if request.db and (path == "/odoo" or path.startswith("/odoo/")):
            target = self._replace_backend_prefix(request.httprequest.full_path)
            return request.redirect(target, 308)
        return super().web_client(s_action=s_action, **kw)


class WhiteLabelManifest(WebManifest):
    def _get_scoped_app_icons(self, app_id):
        icons = super()._get_scoped_app_icons(app_id)
        if any("odoo-icon" in icon.get("src", "") for icon in icons):
            return [
                {
                    "src": "/remove_odoo_bindings/favicon",
                    "sizes": "any",
                    "type": "image/png",
                }
            ]
        return icons

    def _get_webmanifest(self):
        manifest = super()._get_webmanifest()
        company = request.env.company.sudo()
        values = company._white_label_values()
        slug = request.env["ir.http"]._white_label_backend_slug()
        backend_prefix = f"/{slug}"

        manifest.update(
            {
                "name": values["brand_name"],
                "short_name": values["brand_name"],
                "scope": backend_prefix,
                "start_url": backend_prefix,
                "background_color": values["primary_color"],
                "theme_color": values["primary_color"],
                "homepage_url": values["website_url"],
                "icons": [
                    {
                        "src": "/remove_odoo_bindings/favicon",
                        "sizes": "any",
                    }
                ],
            }
        )
        for shortcut in manifest.get("shortcuts", []):
            url = shortcut.get("url", "")
            if url == "/odoo" or url.startswith("/odoo?") or url.startswith("/odoo/"):
                shortcut["url"] = f"{backend_prefix}{url[5:]}"
        return manifest

    @http.route()
    def service_worker(self):
        response = super().service_worker()
        slug = request.env["ir.http"]._white_label_backend_slug()
        body = response.get_data(as_text=True).replace('"/odoo', f'"/{slug}')
        response.set_data(body)
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    @http.route()
    def scoped_app_manifest(self, app_id, path, app_name=""):
        response = super().scoped_app_manifest(app_id, path, app_name=app_name)
        manifest = json.loads(response.get_data(as_text=True))
        values = request.env.company.sudo()._white_label_values()
        manifest.update(
            {
                "background_color": values["primary_color"],
                "theme_color": values["primary_color"],
                "homepage_url": values["website_url"],
            }
        )
        response.set_data(json.dumps(manifest))
        return response


class WhiteLabelAssets(http.Controller):
    @http.route(
        "/remove_odoo_bindings/favicon",
        type="http",
        auth="public",
        methods=["GET"],
        readonly=True,
        sitemap=False,
    )
    def favicon(self):
        company = request.env.company.sudo()
        field_name = "white_label_favicon" if company.white_label_favicon else "logo"
        if not company[field_name]:
            return request.not_found()
        return (
            request.env["ir.binary"]
            .sudo()
            ._get_stream_from(company, field_name)
            .get_response(max_age=86400, immutable=False)
        )
