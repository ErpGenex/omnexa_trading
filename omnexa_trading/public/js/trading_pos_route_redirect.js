/* global frappe */
frappe.provide("omnexa_trading.pos_route_redirect");

omnexa_trading.pos_route_redirect = {
	apply(target) {
		const route = target || {};
		if (route.kind === "list" && route.doctype) {
			frappe.set_route("List", route.doctype, route.filters || {});
			return;
		}
		if (route.kind === "report" && route.report) {
			frappe.set_route("query-report", route.report);
			return;
		}
		frappe.set_route(route.page || "retail-pos");
	},
};
