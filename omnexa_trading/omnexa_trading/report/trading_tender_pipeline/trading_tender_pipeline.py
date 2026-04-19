# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["tt.company = %(company)s", "tt.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("tt.branch = %(branch)s")
	if filters.get("status"):
		conditions.append("tt.status = %(status)s")
	if filters.get("from_date"):
		conditions.append("tt.opening_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("tt.closing_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("tt.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			tt.branch,
			tt.status,
			COUNT(*) AS tender_count,
			COALESCE(SUM(tt.estimated_cost), 0) AS estimated_cost,
			COALESCE(SUM(tt.expected_selling_value), 0) AS expected_selling_value,
			COALESCE(SUM(tt.expected_profit), 0) AS expected_profit
		FROM `tabTrading Tender` tt
		WHERE {' AND '.join(conditions)}
		GROUP BY tt.branch, tt.status
		ORDER BY tt.branch, tt.status
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["estimated_cost"] = flt(row.estimated_cost)
		row["expected_selling_value"] = flt(row.expected_selling_value)
		row["expected_profit"] = flt(row.expected_profit)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Tenders"), "fieldname": "tender_count", "fieldtype": "Int", "width": 90},
		{"label": _("Estimated Cost"), "fieldname": "estimated_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Expected Selling Value"), "fieldname": "expected_selling_value", "fieldtype": "Currency", "width": 160},
		{"label": _("Expected Profit"), "fieldname": "expected_profit", "fieldtype": "Currency", "width": 130},
	]
