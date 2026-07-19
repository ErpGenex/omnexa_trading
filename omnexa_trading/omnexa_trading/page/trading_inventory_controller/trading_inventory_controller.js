frappe.pages["trading-inventory-controller"].on_page_load = function (wrapper) {
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountPharmaDesk) {
		omnexa_core.vertical_portal.mountPharmaDesk(wrapper, "inventory-controller");
		return;
	}
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountRoleDesk) {
		omnexa_core.vertical_portal.mountRoleDesk(wrapper, "omnexa_trading", "inventory-controller");
		return;
	}
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("trading-inventory-controller"),
		single_column: true,
	});
	$(page.body).html("<p class=\"text-muted\">" + __("Load omnexa_core pharma portal desk") + "</p>");
};
