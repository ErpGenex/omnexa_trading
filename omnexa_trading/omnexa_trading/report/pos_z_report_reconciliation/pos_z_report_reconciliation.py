# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""POS Z-report style reconciliation — van sales vs ERP POS sales invoices."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))
	if not filters.get("from_date") or not filters.get("to_date"):
		frappe.throw(_("From Date and To Date are required"))

	params = {
		"company": filters.company,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}
	branch_clause_van = ""
	branch_clause_si = ""
	if filters.get("branch"):
		branch_clause_van = "AND v.branch = %(branch)s"
		branch_clause_si = "AND si.branch = %(branch)s"
		params["branch"] = filters.branch

	van = {
		r.posting_date: flt(r.total)
		for r in frappe.db.sql(
			f"""
			SELECT v.posting_date, SUM(COALESCE(v.grand_total, 0)) AS total
			FROM `tabTrading Van Sales Invoice` v
			WHERE v.company = %(company)s
			  AND v.docstatus = 1
			  AND v.posting_date BETWEEN %(from_date)s AND %(to_date)s
			  {branch_clause_van}
			GROUP BY v.posting_date
			""",
			params,
			as_dict=True,
		)
	}

	pos = {}
	if frappe.db.table_exists("Sales Invoice"):
		pos = {
			r.posting_date: flt(r.total)
			for r in frappe.db.sql(
				f"""
				SELECT si.posting_date, SUM(COALESCE(si.grand_total, 0)) AS total
				FROM `tabSales Invoice` si
				WHERE si.company = %(company)s
				  AND si.docstatus = 1
				  AND IFNULL(si.is_pos, 0) = 1
				  AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
				  {branch_clause_si}
				GROUP BY si.posting_date
				""",
				params,
				as_dict=True,
			)
		}

	dates = sorted(set(van) | set(pos))
	data = []
	for d in dates:
		van_total = flt(van.get(d))
		pos_total = flt(pos.get(d))
		variance = van_total - pos_total
		data.append(
			{
				"posting_date": d,
				"van_sales_total": van_total,
				"pos_invoice_total": pos_total,
				"variance": variance,
				"reconciliation_status": _("Matched") if abs(variance) < 0.01 else _("Review"),
			}
		)

	columns = [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Van Sales (Z)"), "fieldname": "van_sales_total", "fieldtype": "Currency", "width": 130},
		{"label": _("POS Invoices"), "fieldname": "pos_invoice_total", "fieldtype": "Currency", "width": 130},
		{"label": _("Variance"), "fieldname": "variance", "fieldtype": "Currency", "width": 120},
		{"label": _("Status"), "fieldname": "reconciliation_status", "fieldtype": "Data", "width": 100},
	]
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart