frappe.pages["trading-workcenter"].on_page_load = function (wrapper) {
	const OJ = window.OmnexaJourney;
	const VW = window.omnexa_core && omnexa_core.vertical_workcenter;

	if (!OJ || !OJ.mountDeskPage || !VW || !VW.mountJourney) {
		if (VW && VW.mount) {
			VW.mount(wrapper, "omnexa_trading");
			return;
		}
		frappe.ui.make_app_page({ parent: wrapper, title: __("Trading Workcenter"), single_column: true });
		return;
	}

	VW.mountJourney(wrapper, {
		pageTitle: __("Trading Workcenter"),
		shellTitle: OJ.t("مركز عمل Omnexa Trading", "Omnexa Trading Workcenter"),
		shellSubtitle: OJ.t("تجارة وتوزيع · بوابات الأدوار · ديمو صيدلة", "Commerce · role portals · pharma demo"),
		shellRole: OJ.t("مدير النظام", "System Manager"),
		homeRoute: "/app/trading-workcenter",
		sidebarRole: "admin",
		currentPage: "trading-workcenter",
		brandLogoUrl: OJ.tradingLogo,
		portalOpts: { defaultIcon: "📦", portalSubtitleAr: "بوابة خارجية", portalSubtitleEn: "Outpatient portal" },
		async load() {
			const ctx = await OJ.call("omnexa_trading.trading_portal_catalog.get_workcenter_context");
			return {
				...ctx,
				groups: ctx.grouped_portals || [],
				credentials: ctx.demo?.credentials,
			};
		},
		renderIntro($body, data, OJ) {
			$body.append(`<div class="oj-panel oj-phase-panel-intro">
				<h4>${OJ.t("مركز عمل التجارة", "Trading Workcenter")}</h4>
				<p class="oj-muted">${OJ.t(
					"تجارة وتوزيع الأدوية · 7 بوابات أدوار · محاكاة PharmaTrade Egypt",
					"Pharmaceutical trading · 7 role portals · PharmaTrade Egypt simulation"
				)}</p>
			</div>`);
		},
		async renderExtra($body, data, OJ) {
			if (!data.demo?.can_seed) return;
			const $panel = $(`<div class="oj-panel" style="margin-top:16px"></div>`);
			$panel.append(`<h4>${OJ.t("🎯 محاكاة الديمو", "Demo Simulation")}</h4>`);
			$panel.append(`<p class="oj-muted">${OJ.t(
				"إنشاء شركة PharmaTrade Egypt · فرع القاهرة · مستخدمين أدوار · بيانات تجريبية",
				"Creates PharmaTrade Egypt · Cairo branch · role users · sample trading data"
			)}</p>`);
			const $seedBtn = $(`<button type="button" class="oj-btn oj-btn-primary">${OJ.t("تفعيل ديمو الصيدلة", "Activate Pharma Demo")}</button>`);
			$seedBtn.on("click", () => {
				frappe.confirm(
					OJ.t("سيتم إنشاء/تحديث بيانات الديمو. هل تريد المتابعة؟", "This will provision demo data. Continue?"),
					async () => {
						$seedBtn.prop("disabled", true);
						try {
							const res = await OJ.call("omnexa_trading.api.trading_role_demo.run_pharma_demo_setup");
							frappe.show_alert({
								message: res.message || OJ.t("تم التفعيل", "Activated"),
								indicator: "green",
							});
							if (res.result?.message) frappe.msgprint(res.result.message);
							window.location.reload();
						} catch (e) {
							OJ.showCallError(e);
						} finally {
							$seedBtn.prop("disabled", false);
						}
					}
				);
			});
			$panel.append($seedBtn);
			$body.append($panel);
		},
		demoPanelOpts: {
			actionsHtml: "",
		},
		bindActions($body, data, rerender) {
			/* reserved for future sync actions */
		},
	});
};
