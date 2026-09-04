import json
from urllib.parse import urlsplit, urlunsplit

from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.webmanifest import WebManifest
from odoo.http import request


class WhiteLabelHome(Home):
    @staticmethod
    def _replace_backend_location(location):
        if not location or not request.db:
            return location
        slug = request.env["ir.http"]._white_label_backend_slug()
        parsed = urlsplit(location)
        path = f"/{slug}" if parsed.path == "/web" else parsed.path
        return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    @http.route()
    def index(self, s_action=None, db=None, **kw):
        response = super().index(s_action=s_action, db=db, **kw)
        if response.status_code in (301, 302, 303, 307, 308):
            response.headers["Location"] = self._replace_backend_location(
                response.headers.get("Location")
            )
        return response

    @http.route()
    def web_client(self, s_action=None, **kw):
        if request.db and request.httprequest.path == "/web":
            target = self._replace_backend_location(request.httprequest.full_path)
            return request.redirect(target, 308)
        return super().web_client(s_action=s_action, **kw)


class WhiteLabelManifest(WebManifest):
    @http.route()
    def webmanifest(self):
        response = super().webmanifest()
        manifest = json.loads(response.get_data(as_text=True))
        values = request.env.company.sudo()._white_label_values()
        backend_prefix = f"/{request.env['ir.http']._white_label_backend_slug()}"
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
            if url == "/web" or url.startswith("/web?") or url.startswith("/web#"):
                shortcut["url"] = f"{backend_prefix}{url[4:]}"
        response.set_data(json.dumps(manifest))
        return response

    @http.route()
    def service_worker(self):
        response = super().service_worker()
        response.headers["Service-Worker-Allowed"] = "/"
        return response


class WhiteLabelAssets(http.Controller):
    @http.route(
        "/remove_odoo_bindings/favicon",
        type="http",
        auth="public",
        methods=["GET"],
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
