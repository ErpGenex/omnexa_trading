# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class RiskAssessment(Document):
	def validate(self):
		self._validate_risk_dates()
		self._calculate_risk_score()
		self._determine_risk_level()
		self._determine_tolerability()
		self._generate_risk_number()
		self._update_mitigation_status()
	
	def before_save(self):
		self._set_initiated_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_risk_status()
		self._log_submission()
	
	def on_cancel(self):
		self._update_risk_status()
		self._log_cancellation()
	
	def _validate_risk_dates(self):
		"""Validate risk dates"""
		if self.target_completion_date and getdate(self.target_completion_date) < getdate():
			frappe.throw(_("Target Completion Date cannot be in the past"))
	
	def _calculate_risk_score(self):
		"""Calculate risk score based on probability and impact"""
		probability_map = {
			"Very Low (1)": 1,
			"Low (2)": 2,
			"Medium (3)": 3,
			"High (4)": 4,
			"Very High (5)": 5
		}
		
		impact_map = {
			"Negligible (1)": 1,
			"Minor (2)": 2,
			"Moderate (3)": 3,
			"Major (4)": 4,
			"Catastrophic (5)": 5
		}
		
		prob_score = probability_map.get(self.probability, 3)
		impact_score = impact_map.get(self.impact, 3)
		
		self.risk_score = prob_score * impact_score
	
	def _determine_risk_level(self):
		"""Determine risk level based on risk score"""
		if self.risk_score <= 4:
			self.risk_level = "Low"
			self.risk_matrix_position = f"{self.probability} x {self.impact} = {self.risk_score} (Low)"
		elif self.risk_score <= 9:
			self.risk_level = "Medium"
			self.risk_matrix_position = f"{self.probability} x {self.impact} = {self.risk_score} (Medium)"
		elif self.risk_score <= 16:
			self.risk_level = "High"
			self.risk_matrix_position = f"{self.probability} x {self.impact} = {self.risk_score} (High)"
		else:
			self.risk_level = "Extreme"
			self.risk_matrix_position = f"{self.probability} x {self.impact} = {self.risk_score} (Extreme)"
	
	def _determine_tolerability(self):
		"""Determine risk tolerability based on risk level"""
		tolerability_map = {
			"Low": "Acceptable",
			"Medium": "Tolerable with Mitigation",
			"High": "Tolerable with Mitigation",
			"Extreme": "Unacceptable"
		}
		self.tolerability = tolerability_map.get(self.risk_level, "Tolerable with Mitigation")
	
	def _generate_risk_number(self):
		"""Generate unique risk number"""
		if not self.risk_number:
			# Generate risk number based on category and sequence
			category_code = {
				"Quality": "Q",
				"Safety": "S",
				"Compliance": "C",
				"Operational": "O",
				"Financial": "F",
				"Strategic": "ST",
				"Reputation": "R",
				"Environmental": "E",
				"Security": "SEC"
			}
			
			code = category_code.get(self.risk_category, "RSK")
			year = getdate().year
			sequence = frappe.db.count("Risk Assessment", {
				"risk_category": self.risk_category,
				"identification_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.risk_number = f"RSK-{code}-{year}-{sequence:04d}"
	
	def _update_mitigation_status(self):
		"""Update mitigation status based on mitigation actions"""
		if self.mitigation_actions:
			completed = len([a for a in self.mitigation_actions if a.status == "Completed"])
			if completed == len(self.mitigation_actions):
				self.mitigation_status = "Completed"
			elif completed > 0:
				self.mitigation_status = "In Progress"
			else:
				self.mitigation_status = "Not Started"
	
	def _set_initiated_date(self):
		"""Set initiated date if not set"""
		if not self.initiated_date and self.initiated_by:
			self.initiated_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.initiated_by or not self.initiated_date:
			frappe.throw(_("Risk must be initiated and dated before submission"))
		
		if self.risk_status == "Closed":
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required"))
	
	def _update_risk_status(self):
		"""Update risk status based on workflow"""
		if self.docstatus == 1:
			self.risk_status = "Closed"
		elif self.docstatus == 2:
			self.risk_status = "Reopened"
	
	def _log_submission(self):
		"""Log risk submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Close",
			document_type="Risk Assessment",
			document_name=self.name,
			change_reason=f"Risk {self.risk_number} - {self.risk_title} closed"
		)
	
	def _log_cancellation(self):
		"""Log risk cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Reopen",
			document_type="Risk Assessment",
			document_name=self.name,
			change_reason=f"Risk {self.risk_number} - {self.risk_title} reopened"
		)

@frappe.whitelist()
def start_analysis(risk_name):
	"""
	Start risk analysis
	
	Parameters:
	- risk_name: Name of risk assessment
	
	Returns:
	- Success status
	"""
	risk = frappe.get_doc("Risk Assessment", risk_name)
	
	if risk.risk_status != "Open":
		frappe.throw(_("Only open risks can be analyzed"))
	
	risk.risk_status = "Under Analysis"
	risk.save()
	
	return {"success": True, "message": "Risk analysis started"}

@frappe.whitelist()
def complete_analysis(risk_name, risk_causes, contributing_factors="", trigger_events=""):
	"""
	Complete risk analysis
	
	Parameters:
	- risk_name: Name of risk assessment
	- risk_causes: Risk causes
	- contributing_factors: Contributing factors
	- trigger_events: Trigger events
	
	Returns:
	- Success status
	"""
	risk = frappe.get_doc("Risk Assessment", risk_name)
	
	if risk.risk_status != "Under Analysis":
		frappe.throw(_("Only risks under analysis can be completed"))
	
	risk.risk_causes = risk_causes
	risk.contributing_factors = contributing_factors
	risk.trigger_events = trigger_events
	risk.risk_status = "Mitigation In Progress"
	risk.save()
	
	return {"success": True, "message": "Risk analysis completed"}

@frappe.whitelist()
def initiate_mitigation(risk_name, mitigation_strategy):
	"""
	Initiate risk mitigation
	
	Parameters:
	- risk_name: Name of risk assessment
	- mitigation_strategy: Mitigation strategy (Avoid/Reduce/Transfer/Accept)
	
	Returns:
	- Success status
	"""
	risk = frappe.get_doc("Risk Assessment", risk_name)
	
	if risk.risk_status not in ["Mitigation In Progress", "Monitoring"]:
		frappe.throw(_("Only risks in mitigation or monitoring can have mitigation initiated"))
	
	risk.mitigation_strategy = mitigation_strategy
	risk.save()
	
	return {"success": True, "message": "Mitigation initiated"}

@frappe.whitelist()
def complete_mitigation(risk_name, residual_risk, residual_risk_score):
	"""
	Complete risk mitigation
	
	Parameters:
	- risk_name: Name of risk assessment
	- residual_risk: Residual risk level
	- residual_risk_score: Residual risk score
	
	Returns:
	- Success status
	"""
	risk = frappe.get_doc("Risk Assessment", risk_name)
	
	if risk.risk_status != "Mitigation In Progress":
		frappe.throw(_("Only risks with mitigation in progress can be completed"))
	
	risk.residual_risk = residual_risk
	risk.residual_risk_score = residual_risk_score
	
	if residual_risk in ["Low", "Medium"]:
		risk.risk_status = "Monitoring"
	else:
		risk.risk_status = "Mitigation In Progress"
	
	risk.save()
	
	return {"success": True, "message": "Mitigation completed"}

@frappe.whitelist()
def get_risk_summary(category=None, status=None):
	"""
	Get summary of risk assessments
	
	Parameters:
	- category: Filter by category (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if category:
		filters["risk_category"] = category
	if status:
		filters["risk_status"] = status
	
	risks = frappe.get_all("Risk Assessment",
		filters=filters,
		fields=["name", "risk_number", "risk_title", "risk_category", 
		       "risk_status", "risk_level", "risk_score", "identification_date"]
	)
	
	summary = {
		"total": len(risks),
		"by_status": {},
		"by_category": {},
		"by_level": {},
		"average_score": 0,
		"high_risks": [],
		"extreme_risks": []
	}
	
	if risks:
		for risk in risks:
			# Count by status
			summary["by_status"][risk.risk_status] = summary["by_status"].get(risk.risk_status, 0) + 1
			
			# Count by category
			summary["by_category"][risk.risk_category] = summary["by_category"].get(risk.risk_category, 0) + 1
			
			# Count by level
			summary["by_level"][risk.risk_level] = summary["by_level"].get(risk.risk_level, 0) + 1
			
			# Track high and extreme risks
			if risk.risk_level == "High":
				summary["high_risks"].append({
					"risk_number": risk.risk_number,
					"risk_title": risk.risk_title,
					"risk_score": risk.risk_score
				})
			elif risk.risk_level == "Extreme":
				summary["extreme_risks"].append({
					"risk_number": risk.risk_number,
					"risk_title": risk.risk_title,
					"risk_score": risk.risk_score
				})
		
		# Calculate average score
		total_score = sum(r.risk_score for r in risks)
		summary["average_score"] = total_score / len(risks)
	
	return summary

@frappe.whitelist()
def get_risk_register():
	"""
	Get complete risk register
	
	Returns:
	- Risk register data
	"""
	risks = frappe.get_all("Risk Assessment",
		fields=["name", "risk_number", "risk_title", "risk_category", "risk_type",
		       "risk_status", "risk_level", "risk_score", "probability", "impact",
		       "mitigation_strategy", "mitigation_status", "residual_risk",
		       "identification_date", "target_completion_date"],
		order_by="risk_score DESC"
	)
	
	return risks

@frappe.whitelist()
def schedule_risk_review():
	"""
	Schedule risk review for monitoring
	Can be called as a scheduled task
	"""
	today_date = getdate()
	
	risks_due = frappe.get_all("Risk Assessment",
		filters={
			"risk_status": "Monitoring",
			"review_date": ["<=", today_date]
		},
		fields=["name", "risk_number", "risk_title", "review_date"]
	)
	
	for risk in risks_due:
		# Notify monitoring responsible
		risk_doc = frappe.get_doc("Risk Assessment", risk.name)
		
		if risk_doc.monitoring_responsible:
			frappe.sendmail(
				recipients=[risk_doc.monitoring_responsible],
				subject=f"Risk Review Due: {risk_doc.risk_title}",
				message=f"""
				Dear Risk Owner,
				
				The following risk is due for review:
				
				Risk Number: {risk_doc.risk_number}
				Risk Title: {risk_doc.risk_title}
				Risk Level: {risk_doc.risk_level}
				Review Date: {risk_doc.review_date}
				
				Please complete the risk review and update the assessment.
				
				Regards,
				Risk Management
				""",
				reference_doctype="Risk Assessment",
				reference_name=risk_doc.name
			)
	
	return {"success": True, "risks_reviewed": len(risks_due)}
