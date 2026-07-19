# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingVehicleStockTransfer(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_items()
		self._validate_transfer_context()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_items(self):
		for row in self.items or []:
			if flt(row.qty) <= 0:
				frappe.throw(_("Row {0}: Qty must be greater than zero.").format(row.idx), title=_("Transfer"))

	def _validate_transfer_context(self):
		if self.transfer_type == "Load Vehicle" and not self.from_warehouse:
			frappe.throw(_("From Warehouse is required for Load Vehicle."), title=_("Transfer"))
		if self.transfer_type == "Unload Vehicle" and not self.to_warehouse:
			frappe.throw(_("To Warehouse is required for Unload Vehicle."), title=_("Transfer"))

