# Remove Odoo Branding for Odoo 17

This addon replaces visible vendor branding across the Odoo 17 backend, login,
emails, PWA metadata, error dialogs, browser titles, support links, import
screens, and built-in assistant. It also provides a configurable backend entry
slug, such as `/erp` instead of `/web`.

## Included

- Company-scoped product name, favicon, primary color, support links, and footer text
- Database-wide backend URL slug with validation and an automatic `/web` redirect
- Branded browser titles, login pages, offline page, favicon, and PWA manifest
- Branded transactional email footers and report browser titles
- Odoo 17 user-menu and systray controls
- Optional hiding of vendor app-store and theme-store links
- Automated assistant rename
- Safe uninstall cleanup and restoration of the default web application name

## Configuration

1. Install **Remove Odoo Branding**.
2. Open **Settings > General Settings > Remove Odoo Branding**.
3. Enter the product identity, links, color, favicon, assistant name, and backend slug.
4. Save, then reload the browser at the new URL.

The backend slug is database-wide. In multi-database deployments, use a
database filter or separate host name when different databases require different
slugs. The old `/web` backend entry redirects to the configured slug; technical
routes such as `/web/login`, `/web/assets`, and `/web/session` remain available
because they are part of Odoo 17's web protocol.

## Upgrade notes

Version `17.0.2.0.0` replaces the earlier destructive settings and menu
overrides with supported Odoo 17 templates, registry keys, routing APIs, PWA
behavior, and menu hooks. Upgrade the addon after deploying it:

    odoo-bin -d DATABASE -u remove_odoo_bindings --stop-after-init

## Compatibility

- Odoo 17.0 Community and Enterprise
- Dependencies: `base_setup`, `web`, `mail`, and `base_import`
- License: LGPL-3
