# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, nowdate, nowtime

class TemperatureExcursion(Document):
	def validate(self):
		self._validate_excursion_number()
		self._determine_severity()
		self._populate_batch_details()

	def on_submit(self):
		self._quarantine_batch_if_needed()
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self._release_batch_if_quarantined()
		self.db_set("status", "Cancelled")

	def _validate_excursion_number(self):
		"""Validate excursion number is unique"""
		if not self.excursion_number:
			self.excursion_number = f"EXC-{now_datetime().strftime('%Y%m%d')}-{nowtime().replace(':', '')}"
		
		if frappe.db.exists("Temperature Excursion", {
			"excursion_number": self.excursion_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Excursion Number {0} already exists").format(self.excursion_number))

	def _determine_severity(self):
		"""Determine severity based on temperature deviation and duration"""
		if self.min_temperature and self.max_temperature:
			deviation = 0
			if self.temperature < self.min_temperature:
				deviation = self.min_temperature - self.temperature
			elif self.temperature > self.max_temperature:
				deviation = self.temperature - self.max_temperature
			
			# Determine severity based on deviation and duration
			duration = flt(self.duration_minutes or 0)
			if deviation > 10 or (deviation > 5 and duration > 60):
				self.severity = "Critical"
			elif deviation > 5 or (deviation > 3 and duration > 30):
				self.severity = "Major"
			elif deviation > 3 or (deviation > 2 and duration > 15):
				self.severity = "Moderate"
			else:
				self.severity = "Minor"

	def _populate_batch_details(self):
		"""Populate batch details if batch is selected"""
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if not self.item_code:
				self.item_code = batch.item_code
			if not self.warehouse:
				self.warehouse = batch.warehouse
			if not self.company:
				self.company = batch.company

	def _quarantine_batch_if_needed(self):
		"""Quarantine batch if excursion is critical or major"""
		if self.severity in ["Critical", "Major"] and self.batch_affected:
			from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import quarantine_batch
			try:
				quarantine_batch(
					self.batch_number,
					f"Temperature excursion: {self.temperature}°C (Severity: {self.severity})"
				)
				frappe.msgprint(_("Batch {0} quarantined due to temperature excursion").format(self.batch_number))
			except Exception as e:
				frappe.log_error(f"Failed to quarantine batch: {str(e)}", "Temperature Excursion Error")

	def _release_batch_if_quarantined(self):
		"""Release batch if it was quarantined due to this excursion"""
		if self.batch_number and self.disposition == "Release":
			from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import release_quarantined_batch
			try:
				release_quarantined_batch(
					self.batch_number,
					f"Temperature excursion resolved: {self.resolution_notes}"
				)
				frappe.msgprint(_("Batch {0} released from quarantine").format(self.batch_number))
			except Exception as e:
				frappe.log_error(f"Failed to release batch: {str(e)}", "Temperature Excursion Error")

@frappe.whitelist()
def get_open_excursions():
	"""Get all open temperature excursions"""
	excursions = frappe.get_all("Temperature Excursion", {
		"resolution_status": "Open"
	}, ["name", "excursion_number", "excursion_date", "batch_number", "severity", "temperature"])
	
	return excursions

@frappe.whitelist()
def resolve_excursion(excursion_name, resolution_notes, disposition="Quarantine"):
	"""Resolve a temperature excursion"""
	excursion = frappe.get_doc("Temperature Excursion", excursion_name)
	excursion.resolution_status = "Resolved"
	excursion.resolution_date = nowdate()
	excursion.resolved_by = frappe.session.user
	excursion.resolution_notes = resolution_notes
	excursion.disposition = disposition
	excursion.save()
	
	return {"success": True, "message": _("Excursion {0} resolved").format(excursion.excursion_number)}
