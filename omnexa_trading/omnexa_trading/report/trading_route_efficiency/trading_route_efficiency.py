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
	conditions = ["company = %(company)s", "docstatus < 2"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT name, branch, route_date, sales_representative, planned_distance_km, actual_distance_km
		FROM `tabTrading Route Plan`
		WHERE {' AND '.join(conditions)}
		ORDER BY route_date DESC, name DESC
		""",
		filters,
		as_dict=True,
	)
	data = []
	for r in rows:
		planned = flt(r.planned_distance_km)
		actual = flt(r.actual_distance_km)
		eff = (planned / actual * 100.0) if actual > 0 else 0.0
		data.append(
			{
				"route_plan": r.name,
				"branch": r.branch,
				"route_date": r.route_date,
				"sales_representative": r.sales_representative,
				"planned_distance_km": planned,
				"actual_distance_km": actual,
				"route_efficiency_percent": eff,
			}
		)
	return _columns(), data


def _columns():
	return [
		{"label": _("Route Plan"), "fieldname": "route_plan", "fieldtype": "Link", "options": "Trading Route Plan", "width": 150},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Date"), "fieldname": "route_date", "fieldtype": "Date", "width": 100},
		{"label": _("Sales Rep"), "fieldname": "sales_representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 150},
		{"label": _("Planned KM"), "fieldname": "planned_distance_km", "fieldtype": "Float", "width": 100},
		{"label": _("Actual KM"), "fieldname": "actual_distance_km", "fieldtype": "Float", "width": 100},
		{"label": _("Efficiency %"), "fieldname": "route_efficiency_percent", "fieldtype": "Percent", "width": 110},
	]

