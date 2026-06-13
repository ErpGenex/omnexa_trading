frappe.pages["trading-van-sales-pwa"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Van Sales PWA"), single_column: true });
	$(page.body).html(`
		<div class="p-4">
			<h4>${__("Van Sales Field App")}</h4>
			<p class="text-muted">${__("Mobile-optimized van sales — routes, invoices, stock transfers.")}</p>
			<a class="btn btn-primary" href="/app/trading-van-sales-invoice">${__("New Van Sales Invoice")}</a>
			<a class="btn btn-default ml-2" href="/app/trading-route-plan">${__("Route Plans")}</a>
		</div>`);
};
