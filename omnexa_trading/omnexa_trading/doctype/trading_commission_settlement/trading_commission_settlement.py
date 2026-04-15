# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate
from omnexa_trading.utils.gl import post_gl_journal


class TradingCommissionSettlement(Document):
	def validate(self):
		self._validate_period()
		self._validate_context()
		self._calculate_settlement()

	def on_submit(self):
		self._post_commission_journal()
		self.db_set("status", "Settled", update_modified=False)

	def on_cancel(self):
		self._reverse_commission_journal()
		self.db_set("status", "Cancelled", update_modified=False)

	def _validate_period(self):
		if getdate(self.period_to) < getdate(self.period_from):
			frappe.throw(_("Period To cannot be before Period From."), title=_("Commission"))

	def _validate_context(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))
		rep_branch = frappe.db.get_value("Trading Sales Representative", self.sales_representative, "branch")
		if rep_branch and rep_branch != self.branch:
			frappe.throw(_("Sales Representative must belong to same branch."), title=_("Commission"))

	def _calculate_settlement(self):
		values = frappe.db.sql(
			"""
			SELECT
				COALESCE(SUM(grand_total), 0) AS gross_sales,
				COALESCE(SUM(return_amount), 0) AS returns_amount
			FROM `tabTrading Van Sales Invoice`
			WHERE company = %s
			  AND branch = %s
			  AND sales_representative = %s
			  AND posting_date BETWEEN %s AND %s
			  AND docstatus = 1
			""",
			(self.company, self.branch, self.sales_representative, self.period_from, self.period_to),
			as_dict=True,
		)[0]
		self.gross_sales = flt(values.gross_sales, 2)
		self.returns_amount = flt(values.returns_amount, 2)
		self.net_sales = flt(self.gross_sales - self.returns_amount, 2)

		rule = frappe.get_doc("Trading Commission Rule", self.commission_rule)
		self.commission_amount = flt(_commission_for_net_sales(self.net_sales, rule.tiers), 2)

	def _post_commission_journal(self):
		if flt(self.commission_amount) <= 0:
			return
		if not (self.commission_expense_account and self.commission_payable_account):
			frappe.throw(_("Set commission expense and payable accounts before submit."))
		je = post_gl_journal(
			company=self.company,
			branch=self.branch,
			posting_date=self.period_to,
			reference=self.name,
			remarks=f"Commission settlement {self.name}",
			lines=[
				{"account": self.commission_expense_account, "debit": self.commission_amount, "credit": 0},
				{"account": self.commission_payable_account, "debit": 0, "credit": self.commission_amount},
			],
		)
		self.db_set("journal_entry", je, update_modified=False)

	def _reverse_commission_journal(self):
		if self.journal_entry and frappe.db.exists("Journal Entry", self.journal_entry):
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.cancel()


def _commission_for_net_sales(net_sales, tiers):
	net = flt(net_sales)
	if net <= 0:
		return 0
	amount = 0.0
	for row in sorted(tiers, key=lambda x: flt(x.from_amount)):
		from_amt = flt(row.from_amount)
		to_amt = flt(row.to_amount) if flt(row.to_amount) > 0 else net
		if net <= from_amt:
			continue
		eligible = min(net, to_amt) - from_amt
		if eligible > 0:
			amount += eligible * flt(row.rate_percent) / 100.0
	return flt(amount, 2)

