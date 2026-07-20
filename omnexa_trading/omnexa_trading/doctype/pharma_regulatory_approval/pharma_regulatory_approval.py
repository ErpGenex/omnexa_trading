# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, nowdate

class PharmaRegulatoryApproval(Document):
	def validate(self):
		self._validate_approval_number()
		self._validate_license_expiry()
		self._validate_dates()
		self._populate_batch_details()
		self._set_approval_status()

	def on_submit(self):
		self.approved_by = self.approved_by or frappe.session.user
		self.approval_date_2 = self.approval_date_2 or nowdate()
		self.approval_status = "Approved"
		self._update_batch_regulatory_status()
		self._set_workflow_fields()
		self.db_set(
			{
				"status": "Approved",
				"approval_status": "Approved",
				"approved_by": self.approved_by,
				"approval_date_2": self.approval_date_2
	}
		)

	def on_cancel(self):
		self._revert_batch_regulatory_status()
		self.db_set("status", "Cancelled")

	def _validate_approval_number(self):
		"""Validate approval number is unique"""
		if not self.approval_number:
			self.approval_number = f"REG-{now_datetime().strftime('%Y%m%d')}-{self.license_number}"
		
		if frappe.db.exists("Pharma Regulatory Approval", {
			"approval_number": self.approval_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Approval Number {0} already exists").format(self.approval_number))

	def _validate_license_expiry(self):
		"""Validate license is not expired"""
		if self.license_expiry and getdate(self.license_expiry) < getdate():
			frappe.throw(_("License has expired on {0}").format(self.license_expiry))

	def _validate_dates(self):
		"""Validate valid_from and valid_until dates"""
		if self.valid_from and self.valid_until:
			if getdate(self.valid_from) > getdate(self.valid_until):
				frappe.throw(_("Valid From date cannot be after Valid Until date"))

	def _populate_batch_details(self):
		"""Populate batch details if batch is selected"""
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if not self.item_code:
				self.item_code = batch.item_code
			if not self.company:
				self.company = batch.company
			if not self.license_number:
				self.license_number = batch.license_number
			if not self.license_expiry:
				self.license_expiry = batch.license_expiry

	def _set_approval_status(self):
		"""Set approval status based on conditions"""
		if self.status == "Submitted" and not self.approved_by:
			self.approval_status = "Pending"
		elif self.status == "Approved" and self.approved_by:
			self.approval_status = "Approved"
		elif self.status == "Rejected":
			self.approval_status = "Rejected"

	def _update_batch_regulatory_status(self):
		"""Update batch regulatory status on approval"""
		if self.batch_number and self.approval_status == "Approved":
			frappe.db.set_value(
				"Pharma Batch",
				self.batch_number,
				{"regulatory_approval": self.name
	},
				update_modified=True,
			)

	def _revert_batch_regulatory_status(self):
		"""Revert batch regulatory status on cancel"""
		if self.batch_number:
			frappe.db.set_value(
				"Pharma Batch",
				self.batch_number,
				{"regulatory_approval": None
	},
				update_modified=True,
			)

	def _set_workflow_fields(self):
		"""Set workflow fields on submit"""
		if not self.submitted_by:
			self.submitted_by = frappe.session.user
		if not self.submitted_date:
			self.submitted_date = nowdate()
		if self.approval_status == "Approved" and not self.approved_by:
			self.approved_by = frappe.session.user
			self.approval_date_2 = nowdate()

@frappe.whitelist()
def create_regulatory_approval(batch_no, controlled_substance_type, license_number, license_expiry):
	"""Create regulatory approval for a controlled substance batch"""
	batch = frappe.get_doc("Pharma Batch", batch_no)
	
	approval = frappe.new_doc("Pharma Regulatory Approval")
	approval.approval_number = f"REG-{now_datetime().strftime('%Y%m%d')}-{batch_no}"
	approval.approval_date = nowdate()
	approval.batch_number = batch.name
	approval.item_code = batch.item_code
	approval.controlled_substance_type = controlled_substance_type
	approval.license_number = license_number
	approval.license_expiry = license_expiry
	approval.regulatory_authority = "Test Regulatory Authority"
	approval.company = batch.company
	approval.approval_status = "Pending"
	approval.status = "Submitted"
	approval.submitted_by = frappe.session.user
	approval.submitted_date = nowdate()
	
	approval.save()
	
	return approval.name

@frappe.whitelist()
def validate_controlled_substance_sale(batch_no, quantity):
	"""
	Validate if controlled substance sale is allowed
	
	Parameters:
	- batch_no: Batch number
	- quantity: Quantity to sell
	
	Returns:
	- Validation result with message
	"""
	batch = frappe.get_doc("Pharma Batch", batch_no)
	
	# Check if controlled substance
	if not batch.controlled_substance_flag:
		return {"valid": True, "message": "Not a controlled substance"
	}
	
	# Check regulatory approval
	if not batch.regulatory_approval:
		return {"valid": False, "message": "No regulatory approval for controlled substance"
	}
	
	approval = frappe.get_doc("Pharma Regulatory Approval", batch.regulatory_approval)
	
	# Check approval status
	if approval.approval_status != "Approved":
		return {"valid": False, "message": f"Regulatory status is {approval.approval_status}"
	}
	
	# Check license expiry
	if getdate(approval.license_expiry) < getdate():
		return {"valid": False, "message": "License has expired"
	}
	
	# Check validity period
	if approval.valid_from and approval.valid_until:
		today = getdate()
		if today < getdate(approval.valid_from) or today > getdate(approval.valid_until):
			return {"valid": False, "message": "Approval is not valid for current date"
	}
	
	# Check quantity approved
	if approval.quantity_approved and quantity > approval.quantity_approved:
		return {"valid": False, "message": f"Quantity exceeds approved limit of {approval.quantity_approved}"
	}
	
	return {"valid": True, "message": "Controlled substance sale is valid"
	}
