# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class TradingVanSalesInvoice(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_installment_rules()
		self._validate_batch_expiry()
		self._validate_controlled_substances()
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

	def _validate_batch_expiry(self):
		"""Validate batch expiry for all items"""
		from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import _resolve_pharma_batch_name

		for row in self.items or []:
			if not row.batch_no:
				continue

			batch_name = _resolve_pharma_batch_name(row.batch_no, throw=False)
			if not batch_name:
				continue

			batch = frappe.get_doc("Pharma Batch", batch_name)

			if not batch.is_active:
				frappe.throw(_("Batch {0} is not active").format(row.batch_no), title=_("Batch Validation"))

			if batch.quality_status != "Approved":
				frappe.throw(
					_("Batch {0} quality status is {1}. Cannot sell.").format(row.batch_no, batch.quality_status),
					title=_("Batch Validation"),
				)

			if getdate(batch.expiry_date) < getdate():
				frappe.throw(
					_("Batch {0} has expired on {1}").format(row.batch_no, batch.expiry_date),
					title=_("Batch Validation"),
				)

			days_until_expiry = (getdate(batch.expiry_date) - getdate()).days
			if days_until_expiry < 30:
				frappe.msgprint(
					_("Warning: Batch {0} expires in {1} days").format(row.batch_no, days_until_expiry),
					title=_("Near Expiry"),
				)

			if batch.controlled_substance_flag:
				if getdate(batch.license_expiry) < getdate():
					frappe.throw(
						_("Batch {0} is a controlled substance and license has expired").format(row.batch_no),
						title=_("Controlled Substance"),
					)

				from omnexa_trading.omnexa_trading.doctype.pharma_regulatory_approval.pharma_regulatory_approval import (
					validate_controlled_substance_sale,
				)

				validation = validate_controlled_substance_sale(batch.name, row.qty)
				if not validation.get("valid"):
					frappe.throw(_(validation.get("message")), title=_("Controlled Substance"))

	def _validate_controlled_substances(self):
		"""Validate controlled substances require prescription"""
		from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import _resolve_pharma_batch_name

		for row in self.items or []:
			if not row.batch_no:
				continue

			batch_name = _resolve_pharma_batch_name(row.batch_no, throw=False)
			if not batch_name:
				continue

			batch = frappe.get_doc("Pharma Batch", batch_name)

			prescription_number = getattr(self, "prescription_number", None)

			if batch.controlled_substance_flag and not prescription_number:
				frappe.throw(
					_("Prescription is required for controlled substance {0}").format(row.batch_no),
					title=_("Prescription Required"),
				)

			if prescription_number:
				self._validate_prescription(prescription_number, row.batch_no, row.qty)

	def _validate_prescription(self, prescription_number, batch_no, qty):
		"""Validate prescription details"""
		# This is a placeholder for prescription validation logic
		# In a real implementation, this would check against a prescription system
		# For now, we'll just validate that the prescription number is provided
		
		if not prescription_number:
			frappe.throw(_("Prescription number is required for controlled substances"))
		
		# Additional validation could include:
		# - Check prescription expiry
		# - Verify prescribing doctor
		# - Check quantity limits
		# - Verify patient information
		# - Check drug schedule restrictions

	def _set_totals(self):
		net = 0.0
		for row in self.items or []:
			if flt(row.qty) <= 0:
				frappe.throw(_("Row {0}: Qty must be greater than zero.").format(row.idx), title=_("Items"))
			row.amount = flt(flt(row.qty) * flt(row.rate), 2)
			net += flt(row.amount)
		self.net_total = flt(net, 2)
		self.grand_total = flt(self.net_total - flt(self.return_amount), 2)

