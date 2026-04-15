# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, flt, getdate


class TradingInstallmentContract(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_values()
		self._set_finance_amount()
		self._build_schedule()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_values(self):
		if flt(self.principal_amount) <= 0:
			frappe.throw(_("Principal Amount must be greater than zero."))
		if flt(self.down_payment) < 0 or flt(self.down_payment) > flt(self.principal_amount):
			frappe.throw(_("Down Payment must be between zero and principal amount."))
		if int(self.installment_count or 0) <= 0:
			frappe.throw(_("Installment Count must be greater than zero."))

	def _set_finance_amount(self):
		self.finance_amount = flt(flt(self.principal_amount) - flt(self.down_payment), 2)

	def _build_schedule(self):
		self.schedule = []
		base_principal = flt(self.finance_amount) / int(self.installment_count)
		start_date = getdate(self.contract_date)

		for idx in range(int(self.installment_count)):
			due_date = add_months(start_date, idx + 1) if self.installment_frequency == "Monthly" else add_days(start_date, (idx + 1) * 7)
			principal = flt(base_principal, 2)
			interest = flt((principal * flt(self.interest_rate)) / 100.0, 2)
			total_due = flt(principal + interest, 2)
			self.append(
				"schedule",
				{
					"due_date": due_date,
					"principal_amount": principal,
					"interest_amount": interest,
					"penalty_amount": 0,
					"total_due": total_due,
					"status": "Pending",
				},
			)

