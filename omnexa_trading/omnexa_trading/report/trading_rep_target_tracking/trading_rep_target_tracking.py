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
	conditions = ["company = %(company)s"]
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
		SELECT name, rep_name, branch, sales_target_amount, status
		FROM `tabTrading Sales Representative`
		WHERE {' AND '.join(conditions)}
		ORDER BY rep_name
		""",
		filters,
		as_dict=True,
	)

	data = []
	for r in rows:
		data.append(
			{
				"representative": r.name,
				"rep_name": r.rep_name,
				"branch": r.branch,
				"sales_target_amount": flt(r.sales_target_amount),
				"status": r.status,
			}
		)
	return _columns(), data


def _columns():
	return [
		{"label": _("Representative"), "fieldname": "representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 160},
		{"label": _("Name"), "fieldname": "rep_name", "fieldtype": "Data", "width": 170},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Target Amount"), "fieldname": "sales_target_amount", "fieldtype": "Currency", "width": 140},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
	]

