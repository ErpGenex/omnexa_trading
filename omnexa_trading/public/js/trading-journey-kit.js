/**
 * Trading Journey Kit — healthcare-parity desk UI (OmnexaJourney shell override)
 */
/* global frappe */
(function (window) {
	"use strict";
	const OJ = window.OmnexaJourney;
	if (!OJ) return;

	const LOGO = "/assets/omnexa_trading/trading.svg";

	function navigateRoute(route) {
		if (!route || route === "#") return;
		if (route.startsWith("/app/")) {
			window.location.href = route;
			return;
		}
		if (route.startsWith("List/")) {
			frappe.set_route("List", route.slice(5));
			return;
		}
		if (route.startsWith("Form/")) {
			const parts = route.split("/");
			frappe.set_route("Form", parts[1], parts[2] || "");
			return;
		}
		frappe.set_route(route);
	}

	function showCallError(err, fallback) {
		const msg = (err && (err.message || err._error_message)) || fallback || OJ.t("تعذر التحميل", "Could not load data");
		frappe.msgprint({ title: OJ.t("خطأ", "Error"), indicator: "red", message: msg });
	}

	function dataTable(columns, rows) {
		const cols = columns || [];
		const head = cols.map((c) => `<th>${OJ.esc(c.label)}</th>`).join("");
		const body = (rows || [])
			.map((row) => {
				const cells = cols.map((c) => `<td>${OJ.esc(row[c.field] ?? "—")}</td>`).join("");
				return `<tr>${cells}</tr>`;
			})
			.join("");
		return `<div class="oj-table-wrap"><table class="oj-data-table"><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${cols.length || 1}" class="oj-muted">${OJ.t("لا بيانات", "No data")}</td></tr>`}</tbody></table></div>`;
	}

	function bindSidebarNav($root, homeRoute) {
		$root.find(".oj-sidebar-item[data-nav-route]").on("click", function (e) {
			e.preventDefault();
			const route = $(this).attr("data-nav-route");
			if (route) navigateRoute(route);
		});
		$root.find("[data-oj-home]").on("click", function (e) {
			e.preventDefault();
			navigateRoute(homeRoute);
		});
	}

	function installTradingKit() {
		OJ.shell = function (options) {
			const opts = options || {};
			const sidebar = opts.sidebar || OJ.defaultSidebar(opts.sidebarRole || "workcenter", opts.currentPage);
			const navHtml = sidebar
				.map(
					(n) =>
						`<a class="oj-sidebar-item ${n.active ? "active" : ""}" href="#" data-nav-route="${OJ.esc(n.route || "")}"><span class="oj-sidebar-icon">${n.icon || "•"}</span><span>${OJ.esc(n.label)}</span></a>`
				)
				.join("");
			const isRtl = OJ.lang() === "ar";
			const brandLogo = `<img class="oj-brand-logo" src="${OJ.esc(opts.brandLogoUrl || LOGO)}" alt="" />`;
			const $root = $(`<div class="oj-shell oj-desk-page oj-trading-shell ${isRtl ? "oj-rtl" : "oj-ltr"}" dir="${isRtl ? "rtl" : "ltr"}"></div>`);
			const kpiHtml = (opts.kpis || [])
				.map((k) => `<div class="oj-kpi-card"><div class="oj-kpi-value">${OJ.esc(k.value)}</div><div class="oj-kpi-label">${OJ.esc(k.label)}</div></div>`)
				.join("");
			$root.html(`
				<aside class="oj-sidebar">${navHtml}<div class="oj-sidebar-spacer"></div>
					<a class="oj-sidebar-item" href="#" data-oj-home="1">🏠 ${OJ.t("الرئيسية", "Home")}</a>
					<a class="oj-sidebar-item oj-logout" href="/app">⏻ ${OJ.t("خروج", "Logout")}</a>
				</aside>
				<div class="oj-main">
					<header class="oj-topbar">
						<div class="oj-topbar-brand">${brandLogo}<div><strong>ErpGenEx Trading</strong><small>${OJ.esc(opts.subtitle || OJ.t("Commerce Hub", "Commerce Hub"))}</small></div></div>
						<div class="oj-topbar-meta"><span class="oj-pill">${OJ.esc(opts.role || "")}</span><span class="oj-user">${OJ.esc(frappe.session.user_fullname || frappe.session.user)}</span></div>
					</header>
					<div class="oj-title-row"><h1>${OJ.esc(opts.title || "")}</h1></div>
					${kpiHtml ? `<div class="oj-kpi-row">${kpiHtml}</div>` : ""}
					<div class="oj-body"></div>
				</div>`);
			const $body = $root.find(".oj-body");
			if (opts.bodyEl) $body.append(opts.bodyEl);
			else if (opts.body) $body.html(opts.body);
			bindSidebarNav($root, opts.homeRoute || "/app/trading-workcenter");
			return $root;
		};

		function defaultSidebar(role, currentPage) {
			const page = (currentPage || "").replace(/^\/app\//, "");
			const mark = (items) =>
				items.map((item) => ({
					...item,
					active: item.route === `/app/${page}` || (page && item.route.includes(page)),
				}));
			const menus = {
				workcenter: [
					{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/trading-workcenter" },
					{ label: OJ.t("الإدارة التنفيذية", "Executive"), icon: "📊", route: "/app/trading-executive-dashboard" },
					{ label: OJ.t("نقاط البيع", "POS"), icon: "🛒", route: "/app/retail-pos" },
					{ label: OJ.t("مدير المستودع", "Warehouse Manager"), icon: "🏭", route: "/app/trading-warehouse-manager" },
					{ label: OJ.t("مدير الاستيراد", "Import Manager"), icon: "📥", route: "/app/trading-import-manager" },
					{ label: OJ.t("مدير التصدير", "Export Manager"), icon: "📤", route: "/app/trading-export-manager" },
					{ label: OJ.t("مدير الجودة", "Quality Manager"), icon: "🔬", route: "/app/trading-quality-manager" },
				],
				admin: [
					{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🎯", route: "/app/trading-workcenter" },
					{ label: OJ.t("مدير العمليات", "Operations Director"), icon: "⚙️", route: "/app/trading-operations-director" },
					{ label: OJ.t("المندوب الطبي", "Medical Rep"), icon: "🚚", route: "/app/trading-van-sales-pwa" },
					{ label: OJ.t("الاستلام", "Receiving"), icon: "📥", route: "/app/trading-receiving" },
					{ label: OJ.t("التسليم", "Dispatch"), icon: "🚚", route: "/app/trading-dispatch" },
				],
			};
			return mark(menus[role] || menus.workcenter);
		}

		Object.assign(OJ, {
			navigateRoute,
			showCallError,
			dataTable,
			defaultSidebar,
			tradingLogo: LOGO,
		});
	}

	installTradingKit();
})(window);
