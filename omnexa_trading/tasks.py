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

