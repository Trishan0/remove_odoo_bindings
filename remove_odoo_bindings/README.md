# Complete White Label Branding for Odoo 19

This addon replaces visible vendor branding across the Odoo 19 backend, login,
emails, PWA metadata, error dialogs, browser titles, support links, import
screens, and built-in assistant. It also provides a configurable backend URL
slug, such as `/erp` instead of `/odoo`.

## Included

- Company-scoped product name, favicon, primary color, support links, and footer text
- Database-wide backend URL slug with validation and automatic legacy redirects
- Branded browser titles, login pages, offline page, favicon, PWA manifest, and service worker
- Branded transactional email footers and report browser titles
- Current Odoo 19 user-menu and systray controls
- Optional hiding of vendor app-store and theme-store links
- Automated assistant rename
- Safe uninstall cleanup and restoration of the default web application name

## Configuration

1. Install **Complete White Label Branding**.
2. Open **Settings > General Settings > White Label Branding**.
3. Enter the product identity, links, color, favicon, assistant name, and backend slug.
4. Save, then reload the browser.

The backend slug is database-wide. In multi-database deployments, use a
database filter or separate host name when different databases require different
slugs. The old `/odoo` URL redirects to the configured slug; `/web` remains
available for Odoo's technical and compatibility routes.

## Upgrade notes

Version `19.0.2.0.0` replaces the former Odoo 17-era overrides with Odoo 19
templates, registry keys, routing APIs, settings syntax, PWA behavior, and menu
hooks. Upgrade the addon after deploying it:

    odoo-bin -d DATABASE -u remove_odoo_bindings --stop-after-init

## Compatibility

- Odoo 19.0 Community and Enterprise
- Dependencies: `base_setup`, `web`, `mail`, and `base_import`
- License: LGPL-3
