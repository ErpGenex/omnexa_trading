# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingVehicle(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_capacity()
		self._validate_unique_code()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_capacity(self):
		if flt(self.capacity) < 0:
			frappe.throw(_("Capacity cannot be negative."), title=_("Vehicle"))

	def _validate_unique_code(self):
		existing = frappe.db.get_value(
			"Trading Vehicle",
			{"company": self.company, "vehicle_code": self.vehicle_code},
			"name",
		)
		if existing and existing != self.name:
			frappe.throw(_("Vehicle Code must be unique per company."), title=_("Duplicate"))

