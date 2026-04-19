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

	conditions = ["ic.company = %(company)s", "ic.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("ic.branch = %(branch)s")
	if filters.get("status"):
		conditions.append("ic.status = %(status)s")
	if filters.get("from_date"):
		conditions.append("ic.contract_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("ic.contract_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("ic.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			ic.branch,
			ic.status,
			ic.installment_frequency,
			COUNT(*) AS contract_count,
			COALESCE(SUM(ic.principal_amount), 0) AS principal_amount,
			COALESCE(SUM(ic.down_payment), 0) AS down_payment,
			COALESCE(SUM(ic.finance_amount), 0) AS finance_amount,
			COALESCE(SUM(ic.installment_count), 0) AS total_installment_slots
		FROM `tabTrading Installment Contract` ic
		WHERE {' AND '.join(conditions)}
		GROUP BY ic.branch, ic.status, ic.installment_frequency
		ORDER BY ic.branch, ic.status
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["principal_amount"] = flt(row.principal_amount)
		row["down_payment"] = flt(row.down_payment)
		row["finance_amount"] = flt(row.finance_amount)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Frequency"), "fieldname": "installment_frequency", "fieldtype": "Data", "width": 100},
		{"label": _("Contracts"), "fieldname": "contract_count", "fieldtype": "Int", "width": 90},
		{"label": _("Principal"), "fieldname": "principal_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Down Payment"), "fieldname": "down_payment", "fieldtype": "Currency", "width": 120},
		{"label": _("Finance Amount"), "fieldname": "finance_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Installment Slots Σ"), "fieldname": "total_installment_slots", "fieldtype": "Int", "width": 130},
	]
