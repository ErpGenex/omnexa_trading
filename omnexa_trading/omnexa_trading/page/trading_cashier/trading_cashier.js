frappe.pages["trading-cashier"].on_page_load = function (wrapper) {
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountPharmaDesk) {
		omnexa_core.vertical_portal.mountPharmaDesk(wrapper, "cashier");
		return;
	}
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountRoleDesk) {
		omnexa_core.vertical_portal.mountRoleDesk(wrapper, "omnexa_trading", "cashier");
		return;
	}
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("trading-cashier"),
		single_column: true,
	});
	$(page.body).html("<p class=\"text-muted\">" + __("Load omnexa_core pharma portal desk") + "</p>");
};
