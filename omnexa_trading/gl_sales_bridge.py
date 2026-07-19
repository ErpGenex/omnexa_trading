# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""GL bridge for van sales revenue recognition."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_trading.utils.gl import post_gl_journal


@frappe.whitelist()
def sync_van_sales_to_gl(invoice: str) -> dict:
	if not invoice:
		frappe.throw(_("Invoice is required"))
	doc = frappe.get_doc("Trading Van Sales Invoice", invoice)
	if doc.docstatus != 1:
		frappe.throw(_("Invoice must be submitted"))

	revenue_account = frappe.db.get_value("Company", doc.company, "default_income_account")
	if not revenue_account:
		frappe.throw(_("Default income account not set for company"))
	receivable = frappe.db.get_value("Company", doc.company, "default_receivable_account")
	if not receivable:
		frappe.throw(_("Default receivable account not set for company"))

	amount = flt(doc.grand_total)
	je = post_gl_journal(
		company=doc.company,
		branch=doc.branch,
		posting_date=doc.posting_date,
		reference=doc.name,
		remarks=f"Van sales revenue — {doc.name}",
		lines=[
			{"account": receivable, "debit": amount, "credit": 0},
			{"account": revenue_account, "debit": 0, "credit": amount},
		],
	)
	return {"invoice": invoice, "journal_entry": je, "status": "synced"}
