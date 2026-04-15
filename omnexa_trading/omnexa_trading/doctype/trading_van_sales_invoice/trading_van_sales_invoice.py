# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingVanSalesInvoice(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_installment_rules()
		self._set_totals()

	def on_submit(self):
		self.db_set("status", "Submitted", update_modified=False)

	def on_cancel(self):
		self.db_set("status", "Cancelled", update_modified=False)

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_installment_rules(self):
		if self.payment_type == "Installment":
			if not self.installment_plan:
				frappe.throw(_("Installment Plan is required for installment sales."), title=_("Installment"))
			if flt(self.down_payment) < 0:
				frappe.throw(_("Down Payment cannot be negative."), title=_("Installment"))

	def _set_totals(self):
		net = 0.0
		for row in self.items or []:
			if flt(row.qty) <= 0:
				frappe.throw(_("Row {0}: Qty must be greater than zero.").format(row.idx), title=_("Items"))
			row.amount = flt(flt(row.qty) * flt(row.rate), 2)
			net += flt(row.amount)
		self.net_total = flt(net, 2)
		self.grand_total = flt(self.net_total - flt(self.return_amount), 2)

