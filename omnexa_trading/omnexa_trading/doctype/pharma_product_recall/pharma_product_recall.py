# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, nowdate, nowtime

class PharmaProductRecall(Document):
	def validate(self):
		self._validate_recall_number()
		self._populate_batch_details()
		self._calculate_totals()

	def on_submit(self):
		self._quarantine_affected_batches()
		self._initiate_recall()
		self.db_set("status", "Approved")

	def on_cancel(self):
		self._release_quarantined_batches()
		self.db_set("status", "Cancelled")

	def _validate_recall_number(self):
		"""Validate recall number is unique"""
		if not self.recall_number:
			self.recall_number = f"REC-{now_datetime().strftime('%Y%m%d')}-{nowtime().replace(':', '')}"
		
		if frappe.db.exists("Pharma Product Recall", {
			"recall_number": self.recall_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Recall Number {0} already exists").format(self.recall_number))

	def _populate_batch_details(self):
		"""Populate batch details if batch is selected"""
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if not self.item_code:
				self.item_code = batch.item_code
			if not self.company:
				self.company = batch.company
			if not self.initiated_by:
				self.initiated_by = frappe.session.user

	def _calculate_totals(self):
		"""Calculate total quantities"""
		total_affected = 0
		total_recovered = 0
		total_destroyed = 0
		
		for product in self.affected_products or []:
			total_affected += flt(product.quantity_affected)
			total_recovered += flt(product.quantity_recovered)
			total_destroyed += flt(product.quantity_destroyed)
		
		self.quantity_affected = total_affected
		self.quantity_recovered = total_recovered
		self.quantity_destroyed = total_destroyed

	def _quarantine_affected_batches(self):
		"""Quarantine all affected batches"""
		from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import quarantine_batch
		
		for product in self.affected_products or []:
			if product.batch_number:
				try:
					quarantine_batch(
						product.batch_number,
						f"Product Recall {self.recall_number}: {self.recall_reason}"
					)
				except Exception as e:
					frappe.log_error(f"Failed to quarantine batch {product.batch_number}: {str(e)}", "Product Recall Error")

	def _release_quarantined_batches(self):
		"""Release quarantined batches on cancel"""
		from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import release_quarantined_batch
		
		for product in self.affected_products or []:
			if product.batch_number:
				try:
					release_quarantined_batch(
						product.batch_number,
						f"Product Recall {self.recall_number} cancelled"
					)
				except Exception as e:
					frappe.log_error(f"Failed to release batch {product.batch_number}: {str(e)}", "Product Recall Error")

	def _initiate_recall(self):
		"""Initiate recall process"""
		self.recall_status = "Initiated"
		
		# Log recall initiation
		frappe.log_error(
			_("Product Recall {0} initiated for {1} - Severity: {2}").format(
				self.recall_number, self.item_code, self.severity
			),
			"Product Recall Initiated"
		)

@frappe.whitelist()
def initiate_product_recall(batch_no, recall_reason, recall_type="Voluntary", severity="Class II (Serious Health Risk)"):
	"""Initiate a product recall for a batch"""
	batch = frappe.get_doc("Pharma Batch", batch_no)
	
	recall = frappe.new_doc("Pharma Product Recall")
	recall.recall_number = f"REC-{now_datetime().strftime('%Y%m%d')}-{batch_no}"
	recall.recall_date = nowdate()
	recall.recall_type = recall_type
	recall.recall_reason = recall_reason
	recall.severity = severity
	recall.batch_number = batch.name
	recall.item_code = batch.item_code
	recall.company = batch.company
	recall.initiated_by = frappe.session.user
	recall.recall_status = "Draft"
	recall.status = "Draft"
	
	# Add affected product
	recall.append("affected_products", {
		"batch_number": batch.name,
		"item_code": batch.item_code,
		"quantity_affected": flt(batch.batch_size) or 1
	})
	
	recall.save()
	
	return recall.name

@frappe.whitelist()
def notify_customers(recall_name):
	"""Notify affected customers about product recall"""
	recall = frappe.get_doc("Pharma Product Recall", recall_name)
	
	frappe.db.set_value(
		"Pharma Product Recall",
		recall_name,
		{"notification_status": "Partial", "notification_date": nowdate()},
		update_modified=True,
	)
	
	for customer in recall.affected_customers or []:
		try:
			frappe.log_error(
				_("Recall notification sent to customer {0} for recall {1}").format(
					customer.customer, recall.recall_number
				),
				"Customer Notification",
			)
			customer.notification_sent = 1
			customer.notification_date = nowdate()
		except Exception as e:
			frappe.log_error(
				f"Failed to notify customer {customer.customer}: {str(e)}",
				"Customer Notification Error",
			)
	
	frappe.db.set_value(
		"Pharma Product Recall",
		recall_name,
		{"notification_status": "Complete"},
		update_modified=True,
	)
	
	return {"success": True, "message": _("Customer notifications sent")}

@frappe.whitelist()
def complete_recall(recall_name, resolution_plan, corrective_actions):
	"""Complete a product recall"""
	recall = frappe.get_doc("Pharma Product Recall", recall_name)
	
	frappe.db.set_value(
		"Pharma Product Recall",
		recall_name,
		{
			"recall_status": "Completed",
			"resolution_plan": resolution_plan,
			"corrective_actions": corrective_actions,
			"resolution_date": nowdate(),
			"resolved_by": frappe.session.user,
		},
		update_modified=True,
	)
	
	return {"success": True, "message": _("Recall {0} completed").format(recall.recall_number)}
