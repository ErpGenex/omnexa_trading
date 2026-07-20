# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class Deviation(Document):
	def validate(self):
		self._validate_deviation_dates()
		self._validate_root_cause()
		self._generate_deviation_number()
		self._check_capa_requirement()
	
	def before_save(self):
		self._set_reported_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_deviation_status()
		self._create_capa_if_required()
		self._log_submission()
	
	def on_cancel(self):
		self._update_deviation_status()
		self._log_cancellation()
	
	def _validate_deviation_dates(self):
		"""Validate deviation dates"""
		if self.discovery_date and self.occurrence_date:
			if self.discovery_date < self.occurrence_date:
				frappe.throw(_("Discovery Date cannot be before Occurrence Date"))
	
	def _validate_root_cause(self):
		"""Validate that root cause is defined for certain statuses"""
		if self.deviation_status in ["Under Investigation", "Correction In Progress", "Verification Pending", "Closed"]:
			if not self.root_cause:
				frappe.throw(_("Root Cause is required for deviation in this status"))
	
	def _generate_deviation_number(self):
		"""Generate unique deviation number"""
		if not self.deviation_number:
			# Generate deviation number based on category and sequence
			category_code = {
				"Quality": "Q",
				"Safety": "S",
				"Compliance": "C",
				"Operational": "O",
				"Environmental": "E",
				"Security": "SEC"
			}
			
			code = category_code.get(self.deviation_category, "DEV")
			year = getdate().year
			sequence = frappe.db.count("Deviation", {
				"deviation_category": self.deviation_category,
				"occurrence_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.deviation_number = f"DEV-{code}-{year}-{sequence:04d}"
	
	def _check_capa_requirement(self):
		"""Check if CAPA is required based on severity and impact"""
		if self.severity in ["Critical", "Major"]:
			self.capa_required = 1
		elif any([
			self.quality_impact in ["Critical", "Significant"],
			self.safety_impact in ["Critical", "Significant"],
			self.regulatory_impact in ["Critical", "Significant"]
		]):
			self.capa_required = 1
	
	def _set_reported_date(self):
		"""Set reported date if not set"""
		if not self.reported_date and self.reported_by:
			self.reported_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.reported_by or not self.reported_date:
			frappe.throw(_("Deviation must be reported and dated before submission"))
		
		if self.deviation_status in ["Closed", "Verification Pending"]:
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required"))
			
			if not self.qa_approval or not self.qa_approval_date:
				frappe.throw(_("QA Approval is required"))
	
	def _update_deviation_status(self):
		"""Update deviation status based on workflow"""
		if self.docstatus == 1:
			self.deviation_status = "Closed"
		elif self.docstatus == 2:
			self.deviation_status = "Reopened"
	
	def _create_capa_if_required(self):
		"""Create CAPA if required"""
		if self.capa_required and not self.capa_reference:
			# Create CAPA from deviation
			capa = frappe.get_doc({
				"doctype": "CAPA",
				"capa_title": f"CAPA for Deviation: {self.deviation_title
	}",
				"capa_type": "Corrective",
				"capa_category": self.deviation_category,
				"severity": self.severity,
				"initiation_date": getdate(),
				"source_type": "Deviation",
				"source_reference": self.name,
				"source_description": self.deviation_description,
				"source_date": self.occurrence_date,
				"reported_by": self.reported_by,
				"department": self.department,
				"problem_description": self.deviation_description,
				"problem_statement": f"Deviation from expected condition: {self.expected_condition
	}",
				"impact_assessment": self.impact_assessment,
				"risk_level": self.risk_level,
				"root_cause_analysis": self.root_cause_analysis,
				"root_cause": self.root_cause,
				"contributing_factors": self.contributing_factors,
				"initiated_by": self.reported_by
			})
			capa.insert()
			
			# Update deviation with CAPA reference
			self.capa_reference = capa.name
			self.capa_created = 1
			self.capa_date = getdate()
			self.save()
	
	def _log_submission(self):
		"""Log deviation submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Close",
			document_type="Deviation",
			document_name=self.name,
			change_reason=f"Deviation {self.deviation_number} - {self.deviation_title} closed"
		)
	
	def _log_cancellation(self):
		"""Log deviation cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Reopen",
			document_type="Deviation",
			document_name=self.name,
			change_reason=f"Deviation {self.deviation_number} - {self.deviation_title} reopened"
		)

@frappe.whitelist()
def start_investigation(deviation_name):
	"""
	Start deviation investigation
	
	Parameters:
	- deviation_name: Name of deviation
	
	Returns:
	- Success status
	"""
	deviation = frappe.get_doc("Deviation", deviation_name)
	
	if deviation.deviation_status != "Open":
		frappe.throw(_("Only open deviations can be investigated"))
	
	deviation.deviation_status = "Under Investigation"
	deviation.save()
	
	return {"success": True, "message": "Investigation started"
	}

@frappe.whitelist()
def complete_investigation(deviation_name, investigation_findings, root_cause, contributing_factors=""):
	"""
	Complete deviation investigation
	
	Parameters:
	- deviation_name: Name of deviation
	- investigation_findings: Investigation findings
	- root_cause: Root cause
	- contributing_factors: Contributing factors
	
	Returns:
	- Success status
	"""
	deviation = frappe.get_doc("Deviation", deviation_name)
	
	if deviation.deviation_status != "Under Investigation":
		frappe.throw(_("Only deviations under investigation can be completed"))
	
	deviation.investigation_findings = investigation_findings
	deviation.root_cause = root_cause
	deviation.contributing_factors = contributing_factors
	deviation.deviation_status = "Correction In Progress"
	deviation.save()
	
	return {"success": True, "message": "Investigation completed"
	}

@frappe.whitelist()
def complete_correction(deviation_name, immediate_correction, correction_effectiveness):
	"""
	Complete deviation correction
	
	Parameters:
	- deviation_name: Name of deviation
	- immediate_correction: Immediate correction taken
	- correction_effectiveness: Effectiveness of correction
	
	Returns:
	- Success status
	"""
	deviation = frappe.get_doc("Deviation", deviation_name)
	
	if deviation.deviation_status != "Correction In Progress":
		frappe.throw(_("Only deviations with correction in progress can be completed"))
	
	deviation.immediate_correction = immediate_correction
	deviation.correction_effectiveness = correction_effectiveness
	deviation.correction_date = getdate()
	
	if correction_effectiveness == "Effective":
		deviation.deviation_status = "Verification Pending"
	else:
		deviation.deviation_status = "Under Investigation"
	
	deviation.save()
	
	return {"success": True, "message": "Correction completed"
	}

@frappe.whitelist()
def get_deviation_summary(category=None, status=None):
	"""
	Get summary of deviations
	
	Parameters:
	- category: Filter by category (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if category:
		filters["deviation_category"] = category
	if status:
		filters["deviation_status"] = status
	
	deviations = frappe.get_all("Deviation",
		filters=filters,
		fields=["name", "deviation_number", "deviation_title", "deviation_category", 
		       "deviation_status", "deviation_type", "severity", "occurrence_date"]
	)
	
	summary = {
		"total": len(deviations),
		"by_status": {
	},
		"by_category": {
	},
		"by_type": {
	},
		"by_severity": {
	},
		"capa_required": 0,
		"capa_created": 0
	}
	
	for deviation in deviations:
		# Count by status
		summary["by_status"][deviation.deviation_status] = summary["by_status"].get(deviation.deviation_status, 0) + 1
		
		# Count by category
		summary["by_category"][deviation.deviation_category] = summary["by_category"].get(deviation.deviation_category, 0) + 1
		
		# Count by type
		summary["by_type"][deviation.deviation_type] = summary["by_type"].get(deviation.deviation_type, 0) + 1
		
		# Count by severity
		summary["by_severity"][deviation.severity] = summary["by_severity"].get(deviation.severity, 0) + 1
	
	# Count CAPA requirements
	capa_required = frappe.db.count("Deviation", {"capa_required": 1
	})
	capa_created = frappe.db.count("Deviation", {"capa_created": 1
	})
	
	summary["capa_required"] = capa_required
	summary["capa_created"] = capa_created
	
	return summary

@frappe.whitelist()
def get_deviation_trend_analysis(months=12):
	"""
	Get deviation trend analysis
	
	Parameters:
	- months: Number of months to analyze
	
	Returns:
	- Trend analysis data
	"""
	from frappe.utils import add_months
	
	start_date = add_months(getdate(), -months)
	
	deviations = frappe.get_all("Deviation",
		filters={
			"occurrence_date": [">=", start_date]
		},
		fields=["occurrence_date", "deviation_category", "deviation_type", "severity", "deviation_status"]
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
	
	for deviation in deviations:
		month_key = deviation.occurrence_date.strftime("%Y-%m")
		
		# Count by month
		trend_data["by_month"][month_key] = trend_data["by_month"].get(month_key, 0) + 1
		
		# Count by category
		trend_data["by_category"][deviation.deviation_category] = trend_data["by_category"].get(deviation.deviation_category, 0) + 1
		
		# Count by type
		trend_data["by_type"][deviation.deviation_type] = trend_data["by_type"].get(deviation.deviation_type, 0) + 1
		
		# Count by severity
		trend_data["by_severity"][deviation.severity] = trend_data["by_severity"].get(deviation.severity, 0) + 1
	
	# Calculate closure rate
	total_deviations = len(deviations)
	closed_deviations = len([d for d in deviations if d.deviation_status == "Closed"])
	trend_data["closure_rate"] = (closed_deviations / total_deviations * 100) if total_deviations > 0 else 0
	
	return trend_data
