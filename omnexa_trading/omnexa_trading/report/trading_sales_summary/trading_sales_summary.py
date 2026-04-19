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
			name AS van_sales_invoice,
			posting_date,
			branch,
			sales_representative,
			customer_profile,
			payment_type,
			net_total,
			grand_total,
			return_amount,
			(grand_total - return_amount) AS net_after_returns,
			status
		FROM `tabTrading Van Sales Invoice`
		WHERE {' AND '.join(conditions)}
		ORDER BY posting_date DESC, name DESC
		""",
		filters,
		as_dict=True,
	)
	return _columns(), data


def _columns():
	return [
		{"label": _("Invoice"), "fieldname": "van_sales_invoice", "fieldtype": "Link", "options": "Trading Van Sales Invoice", "width": 150},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Sales Representative"), "fieldname": "sales_representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 170},
		{"label": _("Customer"), "fieldname": "customer_profile", "fieldtype": "Link", "options": "Customer Profile", "width": 150},
		{"label": _("Payment Type"), "fieldname": "payment_type", "fieldtype": "Data", "width": 110},
		{"label": _("Net Total"), "fieldname": "net_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Returns"), "fieldname": "return_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Net After Returns"), "fieldname": "net_after_returns", "fieldtype": "Currency", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
	]
