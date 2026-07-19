# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingCommissionRule(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_tiers()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_tiers(self):
		if not self.tiers:
			frappe.throw(_("At least one commission tier is required."), title=_("Commission"))
		sorted_tiers = sorted(self.tiers, key=lambda x: flt(x.from_amount))
		prev_to = None
		for row in sorted_tiers:
			if flt(row.rate_percent) < 0:
				frappe.throw(_("Commission rate cannot be negative."), title=_("Commission"))
			if flt(row.to_amount) and flt(row.to_amount) < flt(row.from_amount):
				frappe.throw(_("Tier To Amount cannot be below From Amount."), title=_("Commission"))
			if prev_to is not None and flt(row.from_amount) < flt(prev_to):
				frappe.throw(_("Commission tiers overlap. Please adjust ranges."), title=_("Commission"))
			prev_to = flt(row.to_amount) if flt(row.to_amount) else prev_to

