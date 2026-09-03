/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { Dialog } from "@web/core/dialog/dialog";
import {
    ClientErrorDialog,
    ErrorDialog,
    NetworkErrorDialog,
    RedirectWarningDialog,
    RPCErrorDialog,
    SessionExpiredDialog,
    WarningDialog,
} from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { session } from "@web/session";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";

// Import the defining modules before removing their registry entries.
import "@web/webclient/user_menu/user_menu_items";
import "@mail/core/web/messaging_menu";
import "@mail/core/web/activity_menu";

const branding = session.white_label || {};
const brandName = branding.brand_name || "Business Suite";
const backendSlug = branding.backend_slug || "erp";
const primaryColor = branding.primary_color || "#2563EB";

document.documentElement.style.setProperty("--white-label-primary", primaryColor);

const userMenuRegistry = registry.category("user_menuitems");
userMenuRegistry.remove("documentation");
userMenuRegistry.remove("odoo_account");
if (!branding.show_help || !branding.support_url) {
    userMenuRegistry.remove("support");
}
if (branding.documentation_url) {
    userMenuRegistry.add("white_label_documentation", () => ({
        type: "item",
        id: "white_label_documentation",
        description: _t("Documentation"),
        href: branding.documentation_url,
        callback: () => browser.open(branding.documentation_url, "_blank"),
        sequence: 10,
    }));
}

const systrayRegistry = registry.category("systray");
if (branding.hide_activities) {
    systrayRegistry.remove("mail.activity_menu");
}
if (branding.hide_messaging) {
    systrayRegistry.remove("mail.messaging_menu");
}

Dialog.defaultProps.title = brandName;
ErrorDialog.title = brandName + " Error";
ClientErrorDialog.title = brandName + " Client Error";
NetworkErrorDialog.title = brandName + " Network Error";
SessionExpiredDialog.title = brandName + " Session Expired";

patch(RPCErrorDialog.prototype, {
    inferTitle() {
        super.inferTitle();
        if (this.title) {
            this.title = this.title.toString().replace(/^Odoo\b/, brandName);
        }
    },
});

patch(WarningDialog.prototype, {
    inferTitle() {
        return super.inferTitle().toString().replace(/^Odoo\b/, brandName);
    },
});

patch(RedirectWarningDialog.prototype, {
    setup() {
        super.setup();
        this.title = this.title.toString().replace(/^Odoo\b/, brandName);
    },
});

patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.title.setParts({ zopenerp: brandName });
    },
});

if (branding.documentation_url) {
    patch(DocumentationLink.prototype, {
        get url() {
            const originalUrl = super.url;
            let parsedUrl;
            try {
                parsedUrl = new URL(originalUrl, browser.location.origin);
            } catch {
                return originalUrl;
            }
            if (
                parsedUrl.hostname !== "odoo.com" &&
                !parsedUrl.hostname.endsWith(".odoo.com")
            ) {
                return originalUrl;
            }
            const relativePath = parsedUrl.pathname
                .replace(/^\/documentation\/(?:latest|[^/]+)\//, "")
                .replace(/^\/+/, "");
            const documentationRoot = branding.documentation_url.replace(/\/*$/, "/");
            return new URL(relativePath, documentationRoot).href;
        },
    });
}

if (backendSlug !== "web") {
    patch(WebClient.prototype, {
        registerServiceWorker() {
            const serviceWorker = browser.navigator.serviceWorker;
            if (!serviceWorker) {
                return;
            }
            return serviceWorker
                .register("/web/service-worker.js", { scope: "/" + backendSlug })
                .then((registration) => {
                    if (registration.active?.state === "activated") {
                        this.serviceWorkerActivatedDeferred.resolve();
                    } else {
                        const worker =
                            registration.installing || registration.waiting || registration.active;
                        worker?.addEventListener("statechange", (event) => {
                            if (event.target.state === "activated") {
                                this.serviceWorkerActivatedDeferred.resolve();
                            }
                        });
                    }
                })
                .catch((error) => {
                    console.error("Service worker registration failed:", error);
                });
        },
    });
}
