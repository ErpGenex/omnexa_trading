import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s", "docstatus < 2"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("posting_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			name AS transfer,
			posting_date,
			branch,
			transfer_type,
			vehicle,
			sales_representative,
			from_warehouse,
			to_warehouse
		FROM `tabTrading Vehicle Stock Transfer`
		WHERE {' AND '.join(conditions)}
		ORDER BY posting_date DESC, name DESC
		""",
		filters,
		as_dict=True,
	)
	return _columns(), data


def _columns():
	return [
		{"label": _("Transfer"), "fieldname": "transfer", "fieldtype": "Link", "options": "Trading Vehicle Stock Transfer", "width": 150},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Transfer Type"), "fieldname": "transfer_type", "fieldtype": "Data", "width": 130},
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Trading Vehicle", "width": 140},
		{"label": _("Sales Representative"), "fieldname": "sales_representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 170},
		{"label": _("From Warehouse"), "fieldname": "from_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
		{"label": _("To Warehouse"), "fieldname": "to_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
	]
