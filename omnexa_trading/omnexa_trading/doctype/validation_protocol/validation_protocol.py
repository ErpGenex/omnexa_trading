# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class ValidationProtocol(Document):
	def validate(self):
		self._validate_protocol_dates()
		self._validate_team_members()
		self._validate_acceptance_criteria()
		self._generate_protocol_number()
		self._update_progress()
	
	def before_save(self):
		self._set_prepared_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_status()
		self._log_submission()
	
	def on_cancel(self):
		self._update_status()
		self._log_cancellation()
	
	def _validate_protocol_dates(self):
		"""Validate protocol dates"""
		if self.planned_start_date and self.planned_end_date:
			if self.planned_start_date > self.planned_end_date:
				frappe.throw(_("Planned Start Date cannot be after Planned End Date"))
		
		if self.actual_start_date and self.actual_end_date:
			if self.actual_start_date > self.actual_end_date:
				frappe.throw(_("Actual Start Date cannot be after Actual End Date"))
	
	def _validate_team_members(self):
		"""Validate that validation team is assigned"""
		if not self.validation_manager:
			frappe.throw(_("Validation Manager is required"))
		
		if not self.qa_approver:
			frappe.throw(_("QA Approver is required"))
	
	def _validate_acceptance_criteria(self):
		"""Validate that acceptance criteria are defined"""
		if not self.acceptance_criteria:
			frappe.throw(_("Acceptance Criteria are required"))
	
	def _generate_protocol_number(self):
		"""Generate unique protocol number"""
		if not self.protocol_number:
			# Generate protocol number based on type and date
			protocol_type_map = {
				"IQ": "DQ",
				"OQ": "OQ",
				"PQ": "PQ",
				"PQV": "PQV",
				"PV": "PV",
				"Validation": "VAL",
				"Revalidation": "REVAL"
			}
			
			prefix = protocol_type_map.get(self.protocol_type, "VAL")
			year = getdate().year
			sequence = frappe.db.count("Validation Protocol", {
				"protocol_type": self.protocol_type,
				"protocol_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.protocol_number = f"{prefix}-{year}-{sequence:04d}"
	
	def _update_progress(self):
		"""Update progress based on test results"""
		if self.test_results:
			total_tests = len(self.test_results)
			completed_tests = len([t for t in self.test_results if t.test_status == "Completed"])
			self.progress_percentage = (completed_tests / total_tests) * 100 if total_tests > 0 else 0
	
	def _set_prepared_date(self):
		"""Set prepared date if not set"""
		if not self.prepared_date and self.prepared_by:
			self.prepared_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.prepared_by or not self.prepared_date:
			frappe.throw(_("Protocol must be prepared and dated before submission"))
		
		if not self.qa_approver:
			frappe.throw(_("QA Approval is required"))
	
	def _update_status(self):
		"""Update protocol status based on workflow"""
		if self.docstatus == 1:
			self.status = "Approved"
		elif self.docstatus == 2:
			self.status = "Cancelled"
	
	def _log_submission(self):
		"""Log protocol submission to audit trail"""
		frappe.get_doc({
			"doctype": "Event Audit Log",
			"event_type": "Submit",
			"document_type": "Validation Protocol",
			"document_name": self.name,
			"event_details": f"Validation Protocol {self.protocol_number} submitted for {self.system_name
	}"
		}).insert()
	
	def _log_cancellation(self):
		"""Log protocol cancellation to audit trail"""
		frappe.get_doc({
			"doctype": "Event Audit Log",
			"event_type": "Cancel",
			"document_type": "Validation Protocol",
			"document_name": self.name,
			"event_details": f"Validation Protocol {self.protocol_number
	} cancelled"
		}).insert()

@frappe.whitelist()
def start_validation_execution(protocol_name):
	"""
	Start validation protocol execution
	
	Parameters:
	- protocol_name: Name of validation protocol
	
	Returns:
	- Success status
	"""
	protocol = frappe.get_doc("Validation Protocol", protocol_name)
	
	if protocol.status != "Approved":
		frappe.throw(_("Only approved protocols can be executed"))
	
	protocol.status = "In Progress"
	protocol.execution_status = "In Progress"
	protocol.actual_start_date = getdate()
	protocol.save()
	
	return {"success": True, "message": "Validation execution started"
	}

@frappe.whitelist()
def complete_validation_execution(protocol_name, execution_summary, deviations="", observations=""):
	"""
	Complete validation protocol execution
	
	Parameters:
	- protocol_name: Name of validation protocol
	- execution_summary: Summary of execution
	- deviations: Any deviations encountered
	- observations: Any observations made
	
	Returns:
	- Success status
	"""
	protocol = frappe.get_doc("Validation Protocol", protocol_name)
	
	if protocol.status != "In Progress":
		frappe.throw(_("Only in-progress protocols can be completed"))
	
	protocol.status = "Completed"
	protocol.execution_status = "Completed"
	protocol.actual_end_date = getdate()
	protocol.execution_summary = execution_summary
	protocol.deviations = deviations
	protocol.observations = observations
	protocol.save()
	
	return {"success": True, "message": "Validation execution completed"
	}

@frappe.whitelist()
def get_validation_summary(system_name=None, validation_type=None):
	"""
	Get summary of validation protocols
	
	Parameters:
	- system_name: Filter by system name (optional)
	- validation_type: Filter by validation type (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if system_name:
		filters["system_name"] = system_name
	if validation_type:
		filters["protocol_type"] = validation_type
	
	protocols = frappe.get_all("Validation Protocol",
		filters=filters,
		fields=["name", "protocol_number", "protocol_type", "status", 
		       "validation_stage", "system_name", "progress_percentage"]
	)
	
	summary = {
		"total": len(protocols),
		"by_status": {
	},
		"by_type": {
	},
		"by_stage": {
	},
		"average_progress": 0
	}
	
	if protocols:
		for protocol in protocols:
			# Count by status
			summary["by_status"][protocol.status] = summary["by_status"].get(protocol.status, 0) + 1
			
			# Count by type
			summary["by_type"][protocol.protocol_type] = summary["by_type"].get(protocol.protocol_type, 0) + 1
			
			# Count by stage
			summary["by_stage"][protocol.validation_stage] = summary["by_stage"].get(protocol.validation_stage, 0) + 1
		
		# Calculate average progress
		total_progress = sum(p.progress_percentage for p in protocols)
		summary["average_progress"] = total_progress / len(protocols)
	
	return summary

@frappe.whitelist()
def create_validation_package(system_name):
	"""
	Create complete validation package for a system
	
	Parameters:
	- system_name: Name of system to validate
	
	Returns:
	- Created protocols
	"""
	protocols = []
	
	# Create IQ Protocol
	iq_protocol = frappe.get_doc({
		"doctype": "Validation Protocol",
		"protocol_title": f"Installation Qualification - {system_name
	}",
		"protocol_type": "IQ",
		"validation_stage": "Installation Qualification",
		"system_name": system_name,
		"validation_level": "Critical",
		"regulatory_standard": "GMP",
		"protocol_date": getdate(),
		"status": "Draft"
	})
	iq_protocol.insert()
	protocols.append(iq_protocol.name)
	
	# Create OQ Protocol
	oq_protocol = frappe.get_doc({
		"doctype": "Validation Protocol",
		"protocol_title": f"Operational Qualification - {system_name
	}",
		"protocol_type": "OQ",
		"validation_stage": "Operational Qualification",
		"system_name": system_name,
		"validation_level": "Critical",
		"regulatory_standard": "GMP",
		"protocol_date": getdate(),
		"status": "Draft"
	})
	oq_protocol.insert()
	protocols.append(oq_protocol.name)
	
	# Create PQ Protocol
	pq_protocol = frappe.get_doc({
		"doctype": "Validation Protocol",
		"protocol_title": f"Performance Qualification - {system_name
	}",
		"protocol_type": "PQ",
		"validation_stage": "Performance Qualification",
		"system_name": system_name,
		"validation_level": "Critical",
		"regulatory_standard": "GMP",
		"protocol_date": getdate(),
		"status": "Draft"
	})
	pq_protocol.insert()
	protocols.append(pq_protocol.name)
	
	return {"success": True, "protocols": protocols
	}
