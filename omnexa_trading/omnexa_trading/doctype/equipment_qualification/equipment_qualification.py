# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class EquipmentQualification(Document):
	def validate(self):
		self._validate_qualification_dates()
		self._validate_team_members()
		self._validate_acceptance_criteria()
		self._generate_qualification_number()
		self._update_progress()
	
	def before_save(self):
		self._set_prepared_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_qualification_status()
		self._log_submission()
	
	def on_cancel(self):
		self._update_qualification_status()
		self._log_cancellation()
	
	def _validate_qualification_dates(self):
		"""Validate qualification dates"""
		if self.planned_start_date and self.planned_end_date:
			if self.planned_start_date > self.planned_end_date:
				frappe.throw(_("Planned Start Date cannot be after Planned End Date"))
		
		if self.actual_start_date and self.actual_end_date:
			if self.actual_start_date > self.actual_end_date:
				frappe.throw(_("Actual Start Date cannot be after Actual End Date"))
	
	def _validate_team_members(self):
		"""Validate that qualification team is assigned"""
		if not self.qualification_manager:
			frappe.throw(_("Qualification Manager is required"))
		
		if not self.qa_approver:
			frappe.throw(_("QA Approver is required"))
	
	def _validate_acceptance_criteria(self):
		"""Validate that acceptance criteria are defined"""
		if not self.acceptance_criteria:
			frappe.throw(_("Acceptance Criteria are required"))
	
	def _generate_qualification_number(self):
		"""Generate unique qualification number"""
		if not self.qualification_number:
			# Generate qualification number based on stage and date
			stage_code = {
				"Design Qualification": "DQ",
				"Installation Qualification": "IQ",
				"Operational Qualification": "OQ",
				"Performance Qualification": "PQ"
			}
			
			code = stage_code.get(self.qualification_stage, "EQ")
			year = getdate().year
			sequence = frappe.db.count("Equipment Qualification", {
				"qualification_stage": self.qualification_stage,
				"qualification_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.qualification_number = f"EQ-{code}-{year}-{sequence:04d}"
	
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
			frappe.throw(_("Qualification must be prepared and dated before submission"))
		
		if not self.qa_approver:
			frappe.throw(_("QA Approval is required"))
	
	def _update_qualification_status(self):
		"""Update qualification status based on workflow"""
		if self.docstatus == 1:
			self.qualification_status = "Completed"
		elif self.docstatus == 2:
			self.qualification_status = "Cancelled"
	
	def _log_submission(self):
		"""Log qualification submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Complete",
			document_type="Equipment Qualification",
			document_name=self.name,
			change_reason=f"Equipment Qualification {self.qualification_number} for {self.equipment_name} completed"
		)
	
	def _log_cancellation(self):
		"""Log qualification cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Cancel",
			document_type="Equipment Qualification",
			document_name=self.name,
			change_reason=f"Equipment Qualification {self.qualification_number} cancelled"
		)

@frappe.whitelist()
def start_qualification_execution(qualification_name):
	"""
	Start equipment qualification execution
	
	Parameters:
	- qualification_name: Name of equipment qualification
	
	Returns:
	- Success status
	"""
	qualification = frappe.get_doc("Equipment Qualification", qualification_name)
	
	if qualification.qualification_status != "Approved":
		frappe.throw(_("Only approved qualifications can be executed"))
	
	qualification.qualification_status = "In Progress"
	qualification.actual_start_date = getdate()
	qualification.save()
	
	return {"success": True, "message": "Qualification execution started"}

@frappe.whitelist()
def complete_qualification_execution(qualification_name, execution_summary, deviations="", observations=""):
	"""
	Complete equipment qualification execution
	
	Parameters:
	- qualification_name: Name of equipment qualification
	- execution_summary: Summary of execution
	- deviations: Any deviations encountered
	- observations: Any observations made
	
	Returns:
	- Success status
	"""
	qualification = frappe.get_doc("Equipment Qualification", qualification_name)
	
	if qualification.qualification_status != "In Progress":
		frappe.throw(_("Only in-progress qualifications can be completed"))
	
	qualification.qualification_status = "Completed"
	qualification.actual_end_date = getdate()
	qualification.deviations = deviations
	qualification.observations = observations
	qualification.save()
	
	return {"success": True, "message": "Qualification execution completed"}

@frappe.whitelist()
def get_qualification_summary(equipment_type=None, stage=None):
	"""
	Get summary of equipment qualifications
	
	Parameters:
	- equipment_type: Filter by equipment type (optional)
	- stage: Filter by qualification stage (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if equipment_type:
		filters["equipment_type"] = equipment_type
	if stage:
		filters["qualification_stage"] = stage
	
	qualifications = frappe.get_all("Equipment Qualification",
		filters=filters,
		fields=["name", "qualification_number", "equipment_name", "equipment_type", 
		       "qualification_stage", "qualification_status", "progress_percentage"]
	)
	
	summary = {
		"total": len(qualifications),
		"by_status": {},
		"by_stage": {},
		"by_type": {},
		"average_progress": 0
	}
	
	if qualifications:
		for qualification in qualifications:
			# Count by status
			summary["by_status"][qualification.qualification_status] = summary["by_status"].get(qualification.qualification_status, 0) + 1
			
			# Count by stage
			summary["by_stage"][qualification.qualification_stage] = summary["by_stage"].get(qualification.qualification_stage, 0) + 1
			
			# Count by type
			summary["by_type"][qualification.equipment_type] = summary["by_type"].get(qualification.equipment_type, 0) + 1
		
		# Calculate average progress
		total_progress = sum(q.progress_percentage for q in qualifications)
		summary["average_progress"] = total_progress / len(qualifications)
	
	return summary

@frappe.whitelist()
def create_equipment_qualification_package(equipment_name, equipment_type):
	"""
	Create complete qualification package for equipment
	
	Parameters:
	- equipment_name: Name of equipment
	- equipment_type: Type of equipment
	
	Returns:
	- Created qualifications
	"""
	qualifications = []
	
	# Create DQ Qualification
	dq_qual = frappe.get_doc({
		"doctype": "Equipment Qualification",
		"qualification_title": f"Design Qualification - {equipment_name}",
		"equipment_name": equipment_name,
		"equipment_type": equipment_type,
		"qualification_stage": "Design Qualification",
		"qualification_type": "Initial Qualification",
		"qualification_date": getdate(),
		"qualification_status": "Draft"
	})
	dq_qual.insert()
	qualifications.append(dq_qual.name)
	
	# Create IQ Qualification
	iq_qual = frappe.get_doc({
		"doctype": "Equipment Qualification",
		"qualification_title": f"Installation Qualification - {equipment_name}",
		"equipment_name": equipment_name,
		"equipment_type": equipment_type,
		"qualification_stage": "Installation Qualification",
		"qualification_type": "Initial Qualification",
		"qualification_date": getdate(),
		"qualification_status": "Draft"
	})
	iq_qual.insert()
	qualifications.append(iq_qual.name)
	
	# Create OQ Qualification
	oq_qual = frappe.get_doc({
		"doctype": "Equipment Qualification",
		"qualification_title": f"Operational Qualification - {equipment_name}",
		"equipment_name": equipment_name,
		"equipment_type": equipment_type,
		"qualification_stage": "Operational Qualification",
		"qualification_type": "Initial Qualification",
		"qualification_date": getdate(),
		"qualification_status": "Draft"
	})
	oq_qual.insert()
	qualifications.append(oq_qual.name)
	
	# Create PQ Qualification
	pq_qual = frappe.get_doc({
		"doctype": "Equipment Qualification",
		"qualification_title": f"Performance Qualification - {equipment_name}",
		"equipment_name": equipment_name,
		"equipment_type": equipment_type,
		"qualification_stage": "Performance Qualification",
		"qualification_type": "Initial Qualification",
		"qualification_date": getdate(),
		"qualification_status": "Draft"
	})
	pq_qual.insert()
	qualifications.append(pq_qual.name)
	
	return {"success": True, "qualifications": qualifications}
