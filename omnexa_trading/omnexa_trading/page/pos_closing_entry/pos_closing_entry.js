frappe.pages["pos-closing-entry"].on_page_load = function () {
	frappe.require("/assets/omnexa_trading/js/trading_pos_route_redirect.js", () => {
		frappe.call({
			method: "omnexa_trading.trading_pos_routes.get_pos_closing_entry_redirect",
			callback(r) {
				omnexa_trading.pos_route_redirect.apply((r && r.message) || {});
			},
		});
	});
};
