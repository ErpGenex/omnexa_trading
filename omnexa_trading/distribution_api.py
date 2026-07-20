# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Trading distribution executive dashboard API."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_distribution_dashboard(company: str | None = None, branch: str | None = None) -> dict[str, Any]:
	filters: dict[str, Any] = {"docstatus": ["<", 2]}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch

	orders = frappe.get_all(
		"Trading Distribution Order",
		filters=filters,
		fields=["name", "status"],
		limit_page_length=5000,
	)
	invoices = frappe.get_all(
		"Trading Van Sales Invoice",
		filters=filters,
		fields=["name", "status", "grand_total"],
		limit_page_length=5000,
	)
	routes = frappe.get_all(
		"Trading Route Plan",
		filters=filters,
		fields=["name", "status"],
		limit_page_length=2000,
	)
	tenders = frappe.get_all(
		"Trading Tender",
		filters=filters,
		fields=["name", "status", "expected_selling_value"],
		limit_page_length=2000,
	)

	def _count_by_status(rows: list[dict]) -> dict[str, int]:
		out: dict[str, int] = {}
		for r in rows:
			st = r.get("status") or "Draft"
			out[st] = out.get(st, 0) + 1
		return out

	return {
		"company": company,
		"branch": branch,
		"orders_total": len(orders),
		"orders_by_status": _count_by_status(orders),
		"invoices_total": len(invoices),
		"invoice_revenue": round(sum(flt(r.get("grand_total")) for r in invoices), 2),
		"routes_total": len(routes),
		"routes_by_status": _count_by_status(routes),
		"tenders_total": len(tenders),
		"tender_pipeline_value": round(sum(flt(r.get("expected_selling_value")) for r in tenders), 2)}
