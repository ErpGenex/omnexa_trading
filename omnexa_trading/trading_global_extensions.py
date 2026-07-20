# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Trading global leader extensions — route AI, commission, credit, IoT, tenders."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def optimize_route_stops(route_plan: str) -> dict:
	if not route_plan:
		frappe.throw(_("Route Plan is required"))
	stops = frappe.get_all(
		"Trading Route Plan Stop",
		filters={"parent": route_plan
	},
		fields=["name", "stop_sequence", "zone", "stop_reference"],
		order_by="stop_sequence asc",
	)
	if len(stops) < 2:
		return {"route_plan": route_plan, "stops": len(stops), "optimized_sequence": [s.name for s in stops]
	}

	ordered = sorted(stops, key=lambda s: (flt(s.stop_sequence), s.name))
	return {
		"route_plan": route_plan,
		"stops": len(stops),
		"optimized_sequence": [s.name for s in ordered],
		"savings_estimate_pct": min(25, max(5, len(stops) * 2))}


@frappe.whitelist()
def compute_commission_forecast(
	sales_representative: str | None = None,
	company: str | None = None,
	months: int = 3,
) -> dict:
	filters: dict[str, Any] = {"docstatus": 1
	}
	if sales_representative:
		filters["sales_representative"] = sales_representative
	if company:
		filters["company"] = company
	invoices = frappe.get_all(
		"Trading Van Sales Invoice",
		filters=filters,
		fields=["name", "grand_total", "posting_date"],
		limit_page_length=5000,
	)
	total = sum(flt(r.get("grand_total")) for r in invoices)
	avg_monthly = total / max(1, months)
	rules = frappe.get_all(
		"Trading Commission Rule",
		filters={"docstatus": ["<", 2], **({"company": company} if company else {})
	},
		fields=["name"],
		limit_page_length=50,
	)
	rate = 0.05
	if rules:
		tiers = frappe.get_all(
			"Trading Commission Tier",
			filters={"parent": rules[0].name
	},
			fields=["rate_percent"],
			order_by="from_amount asc",
			limit_page_length=1,
		)
		if tiers:
			rate = flt(tiers[0].rate_percent) / 100
	return {
		"sales_representative": sales_representative,
		"company": company,
		"historical_revenue": round(total, 2),
		"forecast_monthly_revenue": round(avg_monthly, 2),
		"forecast_commission": round(avg_monthly * rate, 2),
		"commission_rate_pct": round(rate * 100, 2)}


@frappe.whitelist()
def check_customer_credit_limit(customer_profile: str) -> dict:
	if not customer_profile:
		frappe.throw(_("Customer Profile is required"))
	profile = frappe.db.get_value(
		"Customer Profile",
		customer_profile,
		["name", "credit_limit", "company"],
		as_dict=True,
	)
	if not profile:
		frappe.throw(_("Customer Profile not found"))
	limit = flt(profile.get("credit_limit"))
	outstanding = flt(
		frappe.db.sql(
			"""
			SELECT COALESCE(SUM(grand_total), 0)
			FROM `tabTrading Van Sales Invoice`
			WHERE customer_profile = %s AND docstatus = 1 AND status != 'Paid'
			""",
			customer_profile,
		)[0][0]
	)
	available = max(0, limit - outstanding)
	return {
		"customer_profile": customer_profile,
		"credit_limit": limit,
		"outstanding": round(outstanding, 2),
		"available_credit": round(available, 2),
		"within_limit": outstanding <= limit if limit else True
	}


@frappe.whitelist()
def get_van_stock_iot_levels(vehicle: str | None = None, company: str | None = None) -> dict:
	filters: dict[str, Any] = {"docstatus": ["<", 2]}
	if vehicle:
		filters["name"] = vehicle
	if company:
		filters["company"] = company
	vehicles = frappe.get_all(
		"Trading Vehicle",
		filters=filters,
		fields=["name", "vehicle_name", "vehicle_code"],
		limit_page_length=500,
	)
	rows = []
	for v in vehicles:
		transfers = frappe.get_all(
			"Trading Vehicle Stock Transfer",
			filters={"vehicle": v.name, "docstatus": 1
	},
			fields=["name", "modified"],
			order_by="modified desc",
			limit_page_length=1,
		)
		items = frappe.get_all(
			"Trading Vehicle Stock Transfer Item",
			filters={"parent": transfers[0].name} if transfers else {"parent": ""
	},
			fields=["item_code", "qty"],
			limit_page_length=100,
		) if transfers else []
		rows.append(
			{
				"vehicle": v.name,
				"vehicle_name": v.vehicle_name,
				"last_sync": str(transfers[0].modified) if transfers else None,
				"sku_count": len(items),
				"total_qty": round(sum(flt(i.qty) for i in items), 2),
				"iot_status": "online" if transfers else "unknown"
	}
		)
	return {"vehicles": len(rows), "rows": rows
	}


@frappe.whitelist()
def analyze_tender_win_probability(tender: str) -> dict:
	if not tender:
		frappe.throw(_("Tender is required"))
	doc = frappe.get_doc("Trading Tender", tender)
	competitors = frappe.get_all(
		"Trading Tender Competitor",
		filters={"parent": tender
	},
		fields=["competitor_name", "quoted_amount"],
	)
	base = 50.0
	if doc.expected_selling_value and doc.estimated_cost:
		margin = flt(doc.expected_selling_value) - flt(doc.estimated_cost)
		if margin > 0:
			base += min(25, flt(doc.expected_profit_margin_percent) or 10)
		else:
			base -= 10
	base -= min(30, len(competitors) * 5)
	if doc.status in ("Won", "Awarded"):
		base = 95.0
	elif doc.status in ("Lost", "Cancelled"):
		base = 5.0
	return {
		"tender": tender,
		"status": doc.status,
		"competitors": len(competitors),
		"win_probability_pct": round(max(0, min(100, base)), 1),
		"estimated_value": flt(doc.expected_selling_value)
	}
