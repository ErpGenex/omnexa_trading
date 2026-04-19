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
		conditions.append("planned_delivery_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("planned_delivery_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			name,
			branch,
			planned_delivery_date,
			actual_delivery_datetime,
			customer_profile,
			sales_representative,
			total_qty,
			total_amount,
			status
		FROM `tabTrading Distribution Order`
		WHERE {' AND '.join(conditions)}
		ORDER BY planned_delivery_date DESC, name DESC
		""",
		filters,
		as_dict=True,
	)

	data = []
	for row in rows:
		fulfillment_status = "Pending"
		if row.status in ("Cancelled", "Failed"):
			fulfillment_status = row.status
		elif row.actual_delivery_datetime:
			if str(row.actual_delivery_datetime.date()) <= str(row.planned_delivery_date):
				fulfillment_status = "On Time"
			else:
				fulfillment_status = "Late"
		elif row.status == "Delivered":
			fulfillment_status = "Delivered"

		data.append(
			{
				"distribution_order": row.name,
				"branch": row.branch,
				"planned_delivery_date": row.planned_delivery_date,
				"actual_delivery_datetime": row.actual_delivery_datetime,
				"customer_profile": row.customer_profile,
				"sales_representative": row.sales_representative,
				"total_qty": row.total_qty,
				"total_amount": row.total_amount,
				"status": row.status,
				"fulfillment_status": fulfillment_status,
			}
		)
	return _columns(), data


def _columns():
	return [
		{"label": _("Distribution Order"), "fieldname": "distribution_order", "fieldtype": "Link", "options": "Trading Distribution Order", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Planned Date"), "fieldname": "planned_delivery_date", "fieldtype": "Date", "width": 110},
		{"label": _("Actual Datetime"), "fieldname": "actual_delivery_datetime", "fieldtype": "Datetime", "width": 160},
		{"label": _("Customer"), "fieldname": "customer_profile", "fieldtype": "Link", "options": "Customer Profile", "width": 150},
		{"label": _("Sales Representative"), "fieldname": "sales_representative", "fieldtype": "Link", "options": "Trading Sales Representative", "width": 170},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Order Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Fulfillment"), "fieldname": "fulfillment_status", "fieldtype": "Data", "width": 110},
	]
