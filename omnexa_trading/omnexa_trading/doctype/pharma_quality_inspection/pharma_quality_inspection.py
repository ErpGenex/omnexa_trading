# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate, now_datetime

class PharmaQualityInspection(Document):
	def validate(self):
		self._validate_inspection_number()
		self._validate_dates()
		self._validate_batch()
		self._calculate_overall_score()
		self._validate_inspection_status()
		self._populate_batch_details()

	def on_submit(self):
		self._update_batch_quality_status()
		self._set_approval_status()
		self.db_set("status", "Completed")

	def on_cancel(self):
		self._revert_batch_quality_status()
		self.db_set("status", "Cancelled")

	def _validate_inspection_number(self):
		"""Validate inspection number is unique"""
		if not self.inspection_number:
			frappe.throw(_("Inspection Number is required"))
		
		if frappe.db.exists("Pharma Quality Inspection", {
			"inspection_number": self.inspection_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Inspection Number {0} already exists").format(self.inspection_number))

	def _validate_dates(self):
		"""Validate inspection date"""
		if not self.inspection_date:
			frappe.throw(_("Inspection Date is required"))
		
		if getdate(self.inspection_date) > getdate():
			frappe.throw(_("Inspection Date cannot be in the future"))

	def _validate_batch(self):
		"""Validate batch exists and is active"""
		if not self.batch_number:
			frappe.throw(_("Batch Number is required"))
		
		batch = frappe.get_doc("Pharma Batch", self.batch_number)
		
		if not batch.is_active:
			frappe.throw(_("Batch {0} is not active").format(self.batch_number))
		
		if batch.quality_status == "Approved" and self.inspection_type == "Incoming":
			frappe.throw(_("Batch {0} is already approved").format(self.batch_number))
		
		# Populate item and expiry from batch
		if not self.item_code:
			self.item_code = batch.item_code
			self.item_name = batch.item_name
		if not self.batch_expiry:
			self.batch_expiry = batch.expiry_date

	def _calculate_overall_score(self):
		"""Calculate overall score from quality parameters"""
		if self.quality_parameters:
			total_score = 0
			total_weight = 0
			
			for param in self.quality_parameters:
				if param.score and param.weight:
					total_score += flt(param.score) * flt(param.weight)
					total_weight += flt(param.weight)
			
			if total_weight > 0:
				self.overall_score = flt(total_score) / flt(total_weight)
			else:
				self.overall_score = 0

	def _validate_inspection_status(self):
		"""Validate inspection status based on score"""
		if self.overall_score and self.passing_score:
			if self.overall_score >= self.passing_score:
				self.inspection_status = "Passed"
			else:
				self.inspection_status = "Failed"
		
		# Check for critical defects
		if self.defects:
			for defect in self.defects:
				if defect.severity == "Critical":
					self.inspection_status = "Failed"
					break
				elif defect.severity == "Major" and self.inspection_status == "Passed":
					self.inspection_status = "Hold"

	def _populate_batch_details(self):
		"""Populate batch details"""
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if not self.item_code:
				self.item_code = batch.item_code
				self.item_name = batch.item_name
			if not self.batch_expiry:
				self.batch_expiry = batch.expiry_date
			if not self.manufacturer:
				self.manufacturer = batch.manufacturer
			if not self.supplier:
				self.supplier = batch.supplier
			if not self.warehouse:
				self.warehouse = batch.warehouse

	def _update_batch_quality_status(self):
		"""Update batch quality status based on inspection result"""
		if not self.batch_number:
			return

		updates = {"quality_inspection": self.name}

		if self.inspection_status == "Passed":
			updates["quality_status"] = "Approved"
			updates["quality_certificate"] = self.quality_certificate
		elif self.inspection_status == "Failed":
			updates["quality_status"] = "Rejected"
		elif self.inspection_status == "Hold":
			updates.update({
				"quality_status": "Quarantined",
				"quarantine_reason": "Quality Hold",
				"quarantine_date": nowdate(),
			})

		frappe.db.set_value("Pharma Batch", self.batch_number, updates, update_modified=True)

	def _set_approval_status(self):
		"""Set approval status"""
		if self.inspection_status in ["Passed", "Failed", "Hold"]:
			self.approval_status = "Approved"
			self.approved_by = frappe.session.user
			self.approval_date = nowdate()

	def _revert_batch_quality_status(self):
		"""Revert batch quality status on cancel"""
		if not self.batch_number:
			return

		frappe.db.set_value(
			"Pharma Batch",
			self.batch_number,
			{
				"quality_status": "Pending",
				"quality_inspection": None,
				"quality_certificate": None,
				"quarantine_reason": None,
				"quarantine_date": None,
				"release_date": None,
			},
			update_modified=True,
		)

@frappe.whitelist()
def get_pending_inspections():
	"""Get pending quality inspections"""
	inspections = frappe.get_all("Pharma Quality Inspection", {
		"inspection_status": "Pending",
		"status": "Draft"
	}, ["name", "inspection_number", "item_code", "batch_number", "inspection_type", "inspection_date"])
	
	return inspections

@frappe.whitelist()
def create_inspection_from_batch(batch_no, inspection_type="Incoming"):
	"""Create quality inspection from batch"""
	batch = frappe.get_doc("Pharma Batch", batch_no)
	
	inspection = frappe.new_doc("Pharma Quality Inspection")
	inspection.inspection_number = f"QI-{batch_no}-{now_datetime().strftime('%Y%m%d')}"
	inspection.inspection_date = nowdate()
	inspection.inspection_type = inspection_type
	inspection.item_code = batch.item_code
	inspection.item_name = batch.item_name
	inspection.batch_number = batch.name
	inspection.batch_expiry = batch.expiry_date
	inspection.manufacturer = batch.manufacturer
	inspection.supplier = batch.supplier
	inspection.warehouse = batch.warehouse
	inspection.company = batch.company
	inspection.inspector = frappe.session.user
	
	inspection.save()
	
	return inspection.name
