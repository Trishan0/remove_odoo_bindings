/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { router, routerBus, startRouter } from "@web/core/browser/router";
import { titleService } from "@web/core/browser/title_service";
import { Dialog } from "@web/core/dialog/dialog";
import {
    ClientErrorDialog,
    ErrorDialog,
    NetworkErrorDialog,
    RedirectWarningDialog,
    RPCErrorDialog,
    WarningDialog,
} from "@web/core/errors/error_dialogs";
import { rpcBus } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { session } from "@web/session";

// Import the defining modules before removing their registry entries.
import "@web/webclient/user_menu/user_menu_items";
import "@mail/core/public_web/messaging_menu";
import "@mail/core/web/activity_menu";

const branding = session.white_label || {};
const brandName = branding.brand_name || "Business Suite";
const backendSlug = branding.backend_slug || "erp";
const primaryColor = branding.primary_color || "#2563EB";

document.documentElement.style.setProperty("--white-label-primary", primaryColor);

const userMenuRegistry = registry.category("user_menuitems");
userMenuRegistry.remove("odoo_account");
if (!branding.show_help || !branding.support_url) {
    userMenuRegistry.remove("support");
}
if (branding.documentation_url) {
    userMenuRegistry.add("white_label_documentation", () => ({
        type: "item",
        id: "white_label_documentation",
        description: "Documentation",
        href: branding.documentation_url,
        callback: () => browser.open(branding.documentation_url, "_blank"),
        sequence: 21,
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

patch(titleService, {
    start() {
        const service = super.start();
        service.setParts({ whiteLabelBrand: brandName });
        return service;
    },
});

if (backendSlug !== "odoo") {
    patch(router, {
        stateToUrl(state) {
            return super.stateToUrl(state).replace(/^\/odoo(?=\/|\?|$)/, "/" + backendSlug);
        },
        urlToState(url) {
            const normalizedUrl = new URL(url);
            const brandedPrefix = "/" + backendSlug;
            if (
                normalizedUrl.pathname === brandedPrefix ||
                normalizedUrl.pathname.startsWith(brandedPrefix + "/")
            ) {
                normalizedUrl.pathname =
                    "/odoo" + normalizedUrl.pathname.slice(brandedPrefix.length);
            }
            return super.urlToState(normalizedUrl);
        },
    });
    // The core router initializes before addon patches are evaluated. Re-read
    // the initial branded URL after installing the supported conversion hooks.
    startRouter();

    // Odoo 19's delegated anchor handler checks /odoo literally. Mirror that
    // behavior for the branded prefix so internal links keep SPA navigation.
    browser.addEventListener("click", (event) => {
        if (event.defaultPrevented || event.target.closest("[contenteditable]")) {
            return;
        }
        const anchor = event.target.closest("a");
        const href = anchor?.getAttribute("href");
        if (!href || href.startsWith("#") || anchor.target === "_blank") {
            return;
        }
        let url;
        try {
            url = new URL(anchor.href);
        } catch {
            return;
        }
        const brandedPrefix = "/" + backendSlug;
        if (
            browser.location.host === url.host &&
            (browser.location.pathname === brandedPrefix ||
                browser.location.pathname.startsWith(brandedPrefix + "/")) &&
            (url.pathname === brandedPrefix ||
                url.pathname.startsWith(brandedPrefix + "/") ||
                url.pathname === "/web" ||
                url.pathname === "/odoo" ||
                url.pathname.startsWith("/odoo/"))
        ) {
            event.preventDefault();
            const nextState = router.urlToState(url);
            router.pushState(nextState, { replace: true, sync: true });
            routerBus.trigger("ROUTE_CHANGE");
        }
    });

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
                    serviceWorker.ready.then(() => {
                        if (!serviceWorker.controller) {
                            rpcBus.trigger("CLEAR-CACHES");
                        }
                    });
                })
                .catch((error) => {
                    console.error("Service worker registration failed:", error);
                });
        },
    });
}
