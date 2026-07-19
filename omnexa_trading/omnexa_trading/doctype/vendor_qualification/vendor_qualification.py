# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class VendorQualification(Document):
	def validate(self):
		self._validate_qualification_dates()
		self._validate_supplier()
		self._validate_assessment_score()
		self._generate_qualification_number()
		self._set_supplier_name()
	
	def before_save(self):
		self._set_prepared_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_qualification_status()
		self._update_supplier_status()
		self._log_submission()
	
	def on_cancel(self):
		self._update_qualification_status()
		self._log_cancellation()
	
	def _validate_qualification_dates(self):
		"""Validate qualification dates"""
		if self.expiry_date and self.qualification_date:
			if self.expiry_date <= self.qualification_date:
				frappe.throw(_("Expiry Date must be after Qualification Date"))
	
	def _validate_supplier(self):
		"""Validate supplier"""
		if not self.supplier:
			frappe.throw(_("Supplier is required"))
		
		# Check if supplier exists
		if not frappe.db.exists("Supplier", self.supplier):
			frappe.throw(_("Supplier does not exist"))
	
	def _validate_assessment_score(self):
		"""Validate assessment score"""
		if self.qualification_status in ["Qualified", "Approved", "Conditional"]:
			if not self.assessment_score:
				frappe.throw(_("Assessment Score is required for this qualification status"))
			
			if self.assessment_score < 70:
				frappe.throw(_("Assessment Score must be at least 70% for qualification"))
	
	def _generate_qualification_number(self):
		"""Generate unique qualification number"""
		if not self.qualification_number:
			# Generate qualification number based on supplier type and sequence
			type_code = {
				"Manufacturer": "MFG",
				"Distributor": "DST",
				"Service Provider": "SVC",
				"Contractor": "CTR",
				"Consultant": "CON"
			}
			
			code = type_code.get(self.supplier_type, "VQ")
			year = getdate().year
			sequence = frappe.db.count("Vendor Qualification", {
				"supplier_type": self.supplier_type,
				"qualification_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.qualification_number = f"VQ-{code}-{year}-{sequence:04d}"
	
	def _set_supplier_name(self):
		"""Set supplier name from supplier record"""
		if self.supplier and not self.supplier_name:
			supplier = frappe.get_doc("Supplier", self.supplier)
			self.supplier_name = supplier.supplier_name
	
	def _set_prepared_date(self):
		"""Set prepared date if not set"""
		if not self.prepared_date and self.prepared_by:
			self.prepared_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.prepared_by or not self.prepared_date:
			frappe.throw(_("Qualification must be prepared and dated before submission"))
		
		if self.qualification_status in ["Qualified", "Approved"]:
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required"))
			
			if not self.qa_approval or not self.qa_approval_date:
				frappe.throw(_("QA Approval is required"))
	
	def _update_qualification_status(self):
		"""Update qualification status based on workflow"""
		if self.docstatus == 1:
			self.qualification_status = "Qualified"
		elif self.docstatus == 2:
			self.qualification_status = "Disqualified"
	
	def _update_supplier_status(self):
		"""Update supplier qualification status"""
		if self.supplier and self.qualification_status == "Qualified":
			supplier = frappe.get_doc("Supplier", self.supplier)
			supplier.vendor_qualification_status = self.qualification_level
			supplier.vendor_qualification_date = self.qualification_date
			supplier.vendor_qualification_expiry = self.expiry_date
			supplier.save(ignore_permissions=True)
	
	def _log_submission(self):
		"""Log qualification submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Qualify",
			document_type="Vendor Qualification",
			document_name=self.name,
			change_reason=f"Vendor {self.supplier_name} qualified - {self.qualification_level}"
		)
	
	def _log_cancellation(self):
		"""Log qualification cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Disqualify",
			document_type="Vendor Qualification",
			document_name=self.name,
			change_reason=f"Vendor {self.supplier_name} disqualified"
		)

@frappe.whitelist()
def start_assessment(qualification_name):
	"""
	Start vendor assessment
	
	Parameters:
	- qualification_name: Name of vendor qualification
	
	Returns:
	- Success status
	"""
	qualification = frappe.get_doc("Vendor Qualification", qualification_name)
	
	if qualification.qualification_status != "Draft":
		frappe.throw(_("Only draft qualifications can be assessed"))
	
	qualification.qualification_status = "Under Review"
	qualification.assessment_date = getdate()
	qualification.save()
	
	return {"success": True, "message": "Assessment started"}

@frappe.whitelist()
def complete_assessment(qualification_name, assessment_findings, assessment_score, assessment_result):
	"""
	Complete vendor assessment
	
	Parameters:
	- qualification_name: Name of vendor qualification
	- assessment_findings: Assessment findings
	- assessment_score: Assessment score
	- assessment_result: Assessment result (Pass/Fail/Conditional)
	
	Returns:
	- Success status
	"""
	qualification = frappe.get_doc("Vendor Qualification", qualification_name)
	
	if qualification.qualification_status != "Under Review":
		frappe.throw(_("Only qualifications under review can be completed"))
	
	qualification.assessment_findings = assessment_findings
	qualification.assessment_score = assessment_score
	qualification.assessment_result = assessment_result
	
	if assessment_result == "Pass" and assessment_score >= 70:
		qualification.qualification_status = "Approved"
	elif assessment_result == "Conditional":
		qualification.qualification_status = "Conditional"
	else:
		qualification.qualification_status = "Disqualified"
	
	qualification.save()
	
	return {"success": True, "message": "Assessment completed"}

@frappe.whitelist()
def get_vendor_qualification_summary(supplier_type=None, status=None):
	"""
	Get summary of vendor qualifications
	
	Parameters:
	- supplier_type: Filter by supplier type (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if supplier_type:
		filters["supplier_type"] = supplier_type
	if status:
		filters["qualification_status"] = status
	
	qualifications = frappe.get_all("Vendor Qualification",
		filters=filters,
		fields=["name", "qualification_number", "supplier_name", "supplier_type", 
		       "qualification_status", "qualification_level", "assessment_score"]
	)
	
	summary = {
		"total": len(qualifications),
		"by_status": {},
		"by_type": {},
		"by_level": {},
		"average_score": 0
	}
	
	if qualifications:
		for qualification in qualifications:
			# Count by status
			summary["by_status"][qualification.qualification_status] = summary["by_status"].get(qualification.qualification_status, 0) + 1
			
			# Count by type
			summary["by_type"][qualification.supplier_type] = summary["by_type"].get(qualification.supplier_type, 0) + 1
			
			# Count by level
			summary["by_level"][qualification.qualification_level] = summary["by_level"].get(qualification.qualification_level, 0) + 1
		
		# Calculate average score
		total_score = sum(q.assessment_score for q in qualifications if q.assessment_score)
		qualified_count = len([q for q in qualifications if q.assessment_score])
		summary["average_score"] = total_score / qualified_count if qualified_count > 0 else 0
	
	return summary

@frappe.whitelist()
def check_qualification_expiry():
	"""
	Check for expiring vendor qualifications
	Can be called as a scheduled task
	"""
	thirty_days = add_days(getdate(), 30)
	
	expiring_qualifications = frappe.get_all("Vendor Qualification",
		filters={
			"qualification_status": "Qualified",
			"expiry_date": ["<=", thirty_days],
			"expiry_date": [">=", getdate()]
		},
		fields=["name", "qualification_number", "supplier_name", "expiry_date"]
	)
	
	expired_qualifications = frappe.get_all("Vendor Qualification",
		filters={
			"qualification_status": "Qualified",
			"expiry_date": ["<", getdate()]
		},
		fields=["name", "qualification_number", "supplier_name", "expiry_date"]
	)
	
	# Notify QA Manager for expiring qualifications
	qa_managers = frappe.get_all("User", filters={"role": "Pharma Quality Manager"})
	
	if qa_managers and expiring_qualifications:
		for qualification in expiring_qualifications:
			frappe.sendmail(
				recipients=[qa.email for qa in qa_managers],
				subject=f"Vendor Qualification Expiring: {qualification.supplier_name}",
				message=f"""
				Dear QA Manager,
				
				The following vendor qualification is expiring soon:
				
				Qualification Number: {qualification.qualification_number}
				Supplier: {qualification.supplier_name}
				Expiry Date: {qualification.expiry_date}
				
				Please initiate requalification process.
				
				Regards,
				Quality Management
				""",
				reference_doctype="Vendor Qualification",
				reference_name=qualification.name
			)
	
	# Update expired qualifications
	for qualification in expired_qualifications:
		qual_doc = frappe.get_doc("Vendor Qualification", qualification.name)
		qual_doc.qualification_status = "Expired"
		qual_doc.save()
	
	return {
		"success": True,
		"expiring_count": len(expiring_qualifications),
		"expired_count": len(expired_qualifications)
	}
