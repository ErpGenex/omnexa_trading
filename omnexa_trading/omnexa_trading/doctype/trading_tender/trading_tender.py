# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class TradingTender(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_dates()
		self._set_profitability()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_dates(self):
		if self.opening_date and self.closing_date and getdate(self.closing_date) < getdate(self.opening_date):
			frappe.throw(_("Closing Date cannot be before Opening Date."), title=_("Tender"))

	def _set_profitability(self):
		self.expected_profit = flt(flt(self.expected_selling_value) - flt(self.estimated_cost), 2)
		self.expected_profit_margin_percent = (
			flt((flt(self.expected_profit) / flt(self.expected_selling_value)) * 100.0, 2)
			if flt(self.expected_selling_value) > 0
			else 0
		)

