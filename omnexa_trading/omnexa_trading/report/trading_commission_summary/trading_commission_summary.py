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
		conditions.append("period_from >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("period_to <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			name AS settlement,
			branch,
			sales_representative,
			commission_rule,
			period_from,
			period_to,
			gross_sales,
			returns_amount,
			net_sales,
			commission_amount,
			status
		FROM `tabTrading Commission Settlement`
		WHERE {' AND '.join(conditions)}
		ORDER BY period_to DESC, name DESC
		""",
		filters,
		as_dict=True,
	)
	return _columns(), data


def _columns():
	return [
		{"label": _("Settlement"), "fieldname": "settlement", "fieldtype": "Link", "options": "Trading Commission Settlement", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Sales Representative"), "fieldname": "sales_representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 170},
		{"label": _("Commission Rule"), "fieldname": "commission_rule", "fieldtype": "Link", "options": "Trading Commission Rule", "width": 160},
		{"label": _("Period From"), "fieldname": "period_from", "fieldtype": "Date", "width": 110},
		{"label": _("Period To"), "fieldname": "period_to", "fieldtype": "Date", "width": 110},
		{"label": _("Gross Sales"), "fieldname": "gross_sales", "fieldtype": "Currency", "width": 130},
		{"label": _("Returns"), "fieldname": "returns_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Net Sales"), "fieldname": "net_sales", "fieldtype": "Currency", "width": 130},
		{"label": _("Commission"), "fieldname": "commission_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
	]
