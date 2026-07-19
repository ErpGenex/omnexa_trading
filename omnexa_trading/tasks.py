# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe.utils import flt, getdate, today


def process_installment_overdue_penalties():
	contracts = frappe.get_all(
		"Trading Installment Contract",
		filters={"docstatus": 1, "status": ["in", ["Draft", "Active"]]},
		pluck="name",
	)
	current_date = getdate(today())
	for contract_name in contracts:
		contract = frappe.get_doc("Trading Installment Contract", contract_name)
		changed = False
		for row in contract.schedule:
			if row.status == "Paid":
				continue
			if row.due_date and getdate(row.due_date) < current_date:
				row.status = "Overdue"
				base = flt(row.principal_amount) + flt(row.interest_amount)
				row.penalty_amount = flt((base * flt(contract.late_penalty_rate)) / 100.0, 2)
				row.total_due = flt(base + flt(row.penalty_amount), 2)
				changed = True
		if changed:
			contract.status = "Active"
			contract.save(ignore_permissions=True)


def process_expired_batches():
	"""Process expired batches and update their status"""
	from frappe.utils import add_days
	
	today_date = getdate(today())
	
	# Get all active batches that are expired
	expired_batches = frappe.get_all("Pharma Batch", {
		"is_active": 1,
		"expiry_date": ["<", today_date]
	}, ["name", "batch_number", "item_code", "expiry_date"])
	
	for batch in expired_batches:
		batch_doc = frappe.get_doc("Pharma Batch", batch.name)
		batch_doc.is_active = 0
		batch_doc.status = "Expired"
		batch_doc.save(ignore_permissions=True)
		frappe.msgprint(_("Batch {0} marked as expired").format(batch.batch_number))
	
	# Get batches expiring in 30 days (near expiry)
	near_expiry_date = add_days(today_date, 30)
	near_expiry_batches = frappe.get_all("Pharma Batch", {
		"is_active": 1,
		"expiry_date": ["between", [today_date, near_expiry_date]]
	}, ["name", "batch_number", "item_code", "expiry_date"])
	
	# Log near expiry alerts
	for batch in near_expiry_batches:
		frappe.log_error(
			_("Batch {0} (Item: {1}) expires on {2}").format(
				batch.batch_number, batch.item_code, batch.expiry_date
			),
			"Near Expiry Alert"
		)

