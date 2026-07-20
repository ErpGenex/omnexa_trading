# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class CAPA(Document):
	def validate(self):
		self._validate_capa_dates()
		self._validate_root_cause()
		self._validate_actions()
		self._generate_capa_number()
		self._update_action_status()
	
	def before_save(self):
		self._set_initiated_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_capa_status()
		self._log_submission()
	
	def on_cancel(self):
		self._update_capa_status()
		self._log_cancellation()
	
	def _validate_capa_dates(self):
		"""Validate CAPA dates"""
		if self.target_completion_date and getdate(self.target_completion_date) < getdate():
			frappe.throw(_("Target Completion Date cannot be in the past"))
		
		if self.actual_completion_date and self.target_completion_date:
			if self.actual_completion_date > self.target_completion_date:
				self.capa_status = "Overdue"
	
	def _validate_root_cause(self):
		"""Validate that root cause is defined"""
		if self.capa_status in ["Under Investigation", "Actions In Progress", "Verification Pending", "Closed"]:
			if not self.root_cause:
				frappe.throw(_("Root Cause is required for CAPA in this status"))
	
	def _validate_actions(self):
		"""Validate that actions are defined"""
		if self.capa_type in ["Corrective", "Both"] and not self.corrective_actions:
			frappe.throw(_("Corrective Actions are required for this CAPA type"))
		
		if self.capa_type in ["Preventive", "Both"] and not self.preventive_actions:
			frappe.throw(_("Preventive Actions are required for this CAPA type"))
	
	def _generate_capa_number(self):
		"""Generate unique CAPA number"""
		if not self.capa_number:
			# Generate CAPA number based on category and sequence
			category_code = {
				"Quality": "Q",
				"Compliance": "C",
				"Safety": "S",
				"Operational": "O",
				"Documentation": "D",
				"Training": "T",
				"Equipment": "E",
				"Supplier": "SUP"
			}
			
			code = category_code.get(self.capa_category, "CAPA")
			year = getdate().year
			sequence = frappe.db.count("CAPA", {
				"capa_category": self.capa_category,
				"initiation_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.capa_number = f"CAPA-{code}-{year}-{sequence:04d}"
	
	def _update_action_status(self):
		"""Update action status based on individual actions"""
		# Update corrective action status
		if self.corrective_actions:
			corrective_completed = len([a for a in self.corrective_actions if a.status == "Completed"])
			if corrective_completed == len(self.corrective_actions):
				self.corrective_action_status = "Completed"
			elif corrective_completed > 0:
				self.corrective_action_status = "In Progress"
			else:
				self.corrective_action_status = "Not Started"
		
		# Update preventive action status
		if self.preventive_actions:
			preventive_completed = len([a for a in self.preventive_actions if a.status == "Completed"])
			if preventive_completed == len(self.preventive_actions):
				self.preventive_action_status = "Completed"
			elif preventive_completed > 0:
				self.preventive_action_status = "In Progress"
			else:
				self.preventive_action_status = "Not Started"
	
	def _set_initiated_date(self):
		"""Set initiated date if not set"""
		if not self.initiated_date and self.initiated_by:
			self.initiated_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.initiated_by or not self.initiated_date:
			frappe.throw(_("CAPA must be initiated and dated before submission"))
		
		if self.capa_status in ["Closed", "Verification Pending"]:
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required"))
			
			if not self.qa_approval or not self.qa_approval_date:
				frappe.throw(_("QA Approval is required"))
	
	def _update_capa_status(self):
		"""Update CAPA status based on workflow"""
		if self.docstatus == 1:
			self.capa_status = "Closed"
		elif self.docstatus == 2:
			self.capa_status = "Reopened"
	
	def _log_submission(self):
		"""Log CAPA submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Close",
			document_type="CAPA",
			document_name=self.name,
			change_reason=f"CAPA {self.capa_number} - {self.capa_title} closed"
		)
	
	def _log_cancellation(self):
		"""Log CAPA cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Reopen",
			document_type="CAPA",
			document_name=self.name,
			change_reason=f"CAPA {self.capa_number} - {self.capa_title} reopened"
		)

@frappe.whitelist()
def start_investigation(capa_name):
	"""
	Start CAPA investigation
	
	Parameters:
	- capa_name: Name of CAPA
	
	Returns:
	- Success status
	"""
	capa = frappe.get_doc("CAPA", capa_name)
	
	if capa.capa_status != "Open":
		frappe.throw(_("Only open CAPAs can be investigated"))
	
	capa.capa_status = "Under Investigation"
	capa.save()
	
	return {"success": True, "message": "Investigation started"
	}

@frappe.whitelist()
def complete_investigation(capa_name, investigation_findings, root_cause, contributing_factors=""):
	"""
	Complete CAPA investigation
	
	Parameters:
	- capa_name: Name of CAPA
	- investigation_findings: Investigation findings
	- root_cause: Root cause
	- contributing_factors: Contributing factors
	
	Returns:
	- Success status
	"""
	capa = frappe.get_doc("CAPA", capa_name)
	
	if capa.capa_status != "Under Investigation":
		frappe.throw(_("Only CAPAs under investigation can be completed"))
	
	capa.investigation_findings = investigation_findings
	capa.root_cause = root_cause
	capa.contributing_factors = contributing_factors
	capa.capa_status = "Actions In Progress"
	capa.save()
	
	return {"success": True, "message": "Investigation completed"
	}

@frappe.whitelist()
def initiate_verification(capa_name):
	"""
	Initiate CAPA verification
	
	Parameters:
	- capa_name: Name of CAPA
	
	Returns:
	- Success status
	"""
	capa = frappe.get_doc("CAPA", capa_name)
	
	if capa.capa_status != "Actions In Progress":
		frappe.throw(_("Only CAPAs with actions in progress can be verified"))
	
	capa.capa_status = "Verification Pending"
	capa.save()
	
	return {"success": True, "message": "Verification initiated"
	}

@frappe.whitelist()
def complete_verification(capa_name, verification_results, verification_status, effectiveness_score=None):
	"""
	Complete CAPA verification
	
	Parameters:
	- capa_name: Name of CAPA
	- verification_results: Verification results
	- verification_status: Verification status (Verified/Failed)
	- effectiveness_score: Effectiveness score (optional)
	
	Returns:
	- Success status
	"""
	capa = frappe.get_doc("CAPA", capa_name)
	
	if capa.capa_status != "Verification Pending":
		frappe.throw(_("Only CAPAs pending verification can be completed"))
	
	capa.verification_results = verification_results
	capa.verification_status = verification_status
	capa.verification_date = getdate()
	
	if effectiveness_score:
		capa.effectiveness_score = effectiveness_score
		capa.effectiveness_date = getdate()
	
	if verification_status == "Verified":
		capa.capa_status = "Closed"
		capa.actual_completion_date = getdate()
	else:
		capa.capa_status = "Reopened"
	
	capa.save()
	
	return {"success": True, "message": "Verification completed"
	}

@frappe.whitelist()
def get_capa_summary(category=None, status=None):
	"""
	Get summary of CAPAs
	
	Parameters:
	- category: Filter by category (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if category:
		filters["capa_category"] = category
	if status:
		filters["capa_status"] = status
	
	capas = frappe.get_all("CAPA",
		filters=filters,
		fields=["name", "capa_number", "capa_title", "capa_category", 
		       "capa_status", "capa_type", "severity", "initiation_date", "target_completion_date"]
	)
	
	summary = {
		"total": len(capas),
		"by_status": {
	},
		"by_category": {
	},
		"by_type": {
	},
		"by_severity": {
	},
		"overdue": [],
		"upcoming_deadlines": []
	}
	
	today_date = getdate()
	seven_days = add_days(today_date, 7)
	
	for capa in capas:
		# Count by status
		summary["by_status"][capa.capa_status] = summary["by_status"].get(capa.capa_status, 0) + 1
		
		# Count by category
		summary["by_category"][capa.capa_category] = summary["by_category"].get(capa.capa_category, 0) + 1
		
		# Count by type
		summary["by_type"][capa.capa_type] = summary["by_type"].get(capa.capa_type, 0) + 1
		
		# Count by severity
		summary["by_severity"][capa.severity] = summary["by_severity"].get(capa.severity, 0) + 1
		
		# Check overdue
		if capa.target_completion_date and capa.target_completion_date < today_date and capa.capa_status not in ["Closed", "Reopened"]:
			summary["overdue"].append({
				"capa_number": capa.capa_number,
				"capa_title": capa.capa_title,
				"target_completion_date": capa.target_completion_date,
				"severity": capa.severity
			})
		
		# Check upcoming deadlines
		if capa.target_completion_date and capa.target_completion_date >= today_date and capa.target_completion_date <= seven_days and capa.capa_status not in ["Closed", "Reopened"]:
			summary["upcoming_deadlines"].append({
				"capa_number": capa.capa_number,
				"capa_title": capa.capa_title,
				"target_completion_date": capa.target_completion_date,
				"severity": capa.severity
			})
	
	return summary

@frappe.whitelist()
def get_capa_trend_analysis(months=12):
	"""
	Get CAPA trend analysis
	
	Parameters:
	- months: Number of months to analyze
	
	Returns:
	- Trend analysis data
	"""
	from frappe.utils import add_months
	
	start_date = add_months(getdate(), -months)
	
	capas = frappe.get_all("CAPA",
		filters={
			"initiation_date": [">=", start_date]
		},
		fields=["initiation_date", "capa_category", "capa_type", "severity", "capa_status"]
	)
	
	trend_data = {
		"by_month": {
	},
		"by_category": {
	},
		"by_type": {
	},
		"by_severity": {
	},
		"closure_rate": 0
	}
	
	for capa in capas:
		month_key = capa.initiation_date.strftime("%Y-%m")
		
		# Count by month
		trend_data["by_month"][month_key] = trend_data["by_month"].get(month_key, 0) + 1
		
		# Count by category
		trend_data["by_category"][capa.capa_category] = trend_data["by_category"].get(capa.capa_category, 0) + 1
		
		# Count by type
		trend_data["by_type"][capa.capa_type] = trend_data["by_type"].get(capa.capa_type, 0) + 1
		
		# Count by severity
		trend_data["by_severity"][capa.severity] = trend_data["by_severity"].get(capa.severity, 0) + 1
	
	# Calculate closure rate
	total_capas = len(capas)
	closed_capas = len([c for c in capas if c.capa_status == "Closed"])
	trend_data["closure_rate"] = (closed_capas / total_capas * 100) if total_capas > 0 else 0
	
	return trend_data

@frappe.whitelist()
def schedule_capa_reminders():
	"""
	Send reminders for CAPA deadlines
	Can be called as a scheduled task
	"""
	tomorrow = add_days(getdate(), 1)
	
	upcoming_capas = frappe.get_all("CAPA",
		filters={
			"capa_status": ["in", ["Open", "Under Investigation", "Actions In Progress", "Verification Pending"]],
			"target_completion_date": tomorrow
		},
		fields=["name", "capa_number", "capa_title", "target_completion_date", "corrective_action_owner", "preventive_action_owner"]
	)
	
	for capa in upcoming_capas:
		capa_doc = frappe.get_doc("CAPA", capa.name)
		
		# Notify corrective action owner
		if capa_doc.corrective_action_owner:
			frappe.sendmail(
				recipients=[capa_doc.corrective_action_owner],
				subject=f"CAPA Deadline Reminder: {capa_doc.capa_title}",
				message=f"""
				Dear CAPA Owner,
				
				This is a reminder that the following CAPA has a deadline tomorrow:
				
				CAPA Number: {capa_doc.capa_number}
				CAPA Title: {capa_doc.capa_title}
				Target Completion Date: {capa_doc.target_completion_date}
				
				Please ensure all actions are completed on time.
				
				Regards,
				Quality Management
				""",
				reference_doctype="CAPA",
				reference_name=capa_doc.name
			)
	
	return {"success": True, "reminders_sent": len(upcoming_capas)
	}
