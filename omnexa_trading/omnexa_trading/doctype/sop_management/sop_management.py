# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class SOPManagement(Document):
	def validate(self):
		self._validate_sop_dates()
		self._validate_approvals()
		self._generate_sop_number()
		self._update_version_history()
		self._calculate_review_date()
	
	def before_save(self):
		self._set_prepared_date()
	
	def on_submit(self):
		self._validate_required_approvals()
		self._update_sop_status()
		self._distribute_sop()
		self._log_submission()
	
	def on_cancel(self):
		self._update_sop_status()
		self._log_cancellation()
	
	def _validate_sop_dates(self):
		"""Validate SOP dates"""
		if self.effective_date and self.review_date:
			if self.effective_date > self.review_date:
				frappe.throw(_("Effective Date cannot be after Review Date"))
		
		if self.effective_date and self.expiry_date:
			if self.effective_date > self.expiry_date:
				frappe.throw(_("Effective Date cannot be after Expiry Date"))
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.prepared_by:
			frappe.throw(_("Prepared By is required"))
		
		if self.sop_status in ["Approved", "Published"]:
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required for approved SOPs"))
	
	def _generate_sop_number(self):
		"""Generate unique SOP number"""
		if not self.sop_number:
			# Generate SOP number based on category and sequence
			category_code = {
				"Quality": "Q",
				"Operations": "O",
				"Safety": "S",
				"Compliance": "C",
				"Training": "T",
				"IT": "I",
				"HR": "H",
				"Finance": "F",
				"Maintenance": "M"
			}
			
			code = category_code.get(self.sop_category, "X")
			year = getdate().year
			sequence = frappe.db.count("SOP Management", {
				"sop_category": self.sop_category,
				"prepared_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.sop_number = f"SOP-{code}-{year}-{sequence:04d}"
	
	def _update_version_history(self):
		"""Update version history when SOP is modified"""
		if self.change_reason and self.change_description:
			version_entry = {
				"version": self.current_version,
				"change_date": getdate(),
				"change_reason": self.change_reason,
				"change_description": self.change_description,
				"changed_by": frappe.session.user
			}
			
			if not self.version_history:
				self.version_history = []
			
			self.version_history.append(version_entry)
	
	def _calculate_review_date(self):
		"""Calculate review date if not set"""
		if self.effective_date and not self.review_date:
			# Default review date is 1 year from effective date
			self.review_date = add_days(self.effective_date, 365)
	
	def _set_prepared_date(self):
		"""Set prepared date if not set"""
		if not self.prepared_date and self.prepared_by:
			self.prepared_date = getdate()
	
	def _validate_required_approvals(self):
		"""Validate that all required approvals are in place before submission"""
		if not self.prepared_by or not self.prepared_date:
			frappe.throw(_("SOP must be prepared and dated before submission"))
		
		if self.sop_status in ["Approved", "Published"]:
			if not self.approved_by or not self.approved_date:
				frappe.throw(_("Approved By and Approved Date are required"))
			
			if not self.qa_approval or not self.qa_approval_date:
				frappe.throw(_("QA Approval is required for approved SOPs"))
	
	def _update_sop_status(self):
		"""Update SOP status based on workflow"""
		if self.docstatus == 1:
			self.sop_status = "Published"
		elif self.docstatus == 2:
			self.sop_status = "Withdrawn"
	
	def _distribute_sop(self):
		"""Distribute SOP to distribution list"""
		if self.distribution_list and self.sop_status == "Published":
			for recipient in self.distribution_list:
				if recipient.email:
					# Send notification to recipient
					frappe.sendmail(
						recipients=[recipient.email],
						subject=f"New SOP Published: {self.sop_title}",
						message=f"""
						Dear {recipient.recipient_name},
						
						A new SOP has been published and requires your attention:
						
						SOP Number: {self.sop_number}
						SOP Title: {self.sop_title}
						Effective Date: {self.effective_date}
						
						Please review and acknowledge receipt.
						
						Regards,
						Quality Management
						""",
						reference_doctype=self.doctype,
						reference_name=self.name
					)
	
	def _log_submission(self):
		"""Log SOP submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Publish",
			document_type="SOP Management",
			document_name=self.name,
			change_reason=f"SOP {self.sop_number} - {self.sop_title} published"
		)
	
	def _log_cancellation(self):
		"""Log SOP cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Withdraw",
			document_type="SOP Management",
			document_name=self.name,
			change_reason=f"SOP {self.sop_number} - {self.sop_title} withdrawn"
		)

@frappe.whitelist()
def create_sop_revision(sop_name, change_reason, change_description):
	"""
	Create a new revision of an existing SOP
	
	Parameters:
	- sop_name: Name of SOP to revise
	- change_reason: Reason for revision
	- change_description: Description of changes
	
	Returns:
	- New SOP name
	"""
	sop = frappe.get_doc("SOP Management", sop_name)
	
	# Create new revision
	new_sop = frappe.copy_doc(sop)
	new_sop.sop_status = "Draft"
	new_sop.current_version = str(float(sop.current_version) + 0.1)
	new_sop.change_reason = change_reason
	new_sop.change_description = change_description
	new_sop.prepared_by = frappe.session.user
	new_sop.prepared_date = getdate()
	new_sop.effective_date = None
	new_sop.approved_by = None
	new_sop.approved_date = None
	new_sop.qa_approval = None
	new_sop.qa_approval_date = None
	new_sop.insert()
	
	# Mark original as superseded
	sop.sop_status = "Superseded"
	sop.save()
	
	return {"success": True, "new_sop": new_sop.name}

@frappe.whitelist()
def acknowledge_sop(sop_name):
	"""
	Acknowledge receipt of an SOP
	
	Parameters:
	- sop_name: Name of SOP to acknowledge
	
	Returns:
	- Success status
	"""
	sop = frappe.get_doc("SOP Management", sop_name)
	
	# Check if user is in distribution list
	user_email = frappe.session.user
	in_distribution = False
	
	for recipient in sop.distribution_list:
		if recipient.email == user_email:
			recipient.acknowledgement_date = getdate()
			recipient.acknowledgement_status = "Acknowledged"
			in_distribution = True
			break
	
	if not in_distribution:
		frappe.throw(_("You are not in the distribution list for this SOP"))
	
	sop.save()
	
	return {"success": True, "message": "SOP acknowledged successfully"}

@frappe.whitelist()
def get_sop_summary(category=None, status=None):
	"""
	Get summary of SOPs
	
	Parameters:
	- category: Filter by category (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if category:
		filters["sop_category"] = category
	if status:
		filters["sop_status"] = status
	
	sops = frappe.get_all("SOP Management",
		filters=filters,
		fields=["name", "sop_number", "sop_title", "sop_category", 
		       "sop_status", "current_version", "effective_date", "review_date"]
	)
	
	summary = {
		"total": len(sops),
		"by_status": {},
		"by_category": {},
		"expiring_soon": [],
		"overdue_review": []
	}
	
	today_date = getdate()
	thirty_days = add_days(today_date, 30)
	
	for sop in sops:
		# Count by status
		summary["by_status"][sop.sop_status] = summary["by_status"].get(sop.sop_status, 0) + 1
		
		# Count by category
		summary["by_category"][sop.sop_category] = summary["by_category"].get(sop.sop_category, 0) + 1
		
		# Check expiring soon
		if sop.expiry_date and sop.expiry_date <= thirty_days:
			summary["expiring_soon"].append({
				"sop_number": sop.sop_number,
				"sop_title": sop.sop_title,
				"expiry_date": sop.expiry_date
			})
		
		# Check overdue review
		if sop.review_date and sop.review_date < today_date:
			summary["overdue_review"].append({
				"sop_number": sop.sop_number,
				"sop_title": sop.sop_title,
				"review_date": sop.review_date
			})
	
	return summary

@frappe.whitelist()
def schedule_sop_review():
	"""
	Schedule review for SOPs due for review
	Can be called as a scheduled task
	"""
	today_date = getdate()
	
	sops_due = frappe.get_all("SOP Management",
		filters={
			"sop_status": "Published",
			"review_date": ["<=", today_date]
		},
		fields=["name", "sop_number", "sop_title", "review_date"]
	)
	
	for sop in sops_due:
		# Send notification to QA Manager
		qa_managers = frappe.get_all("User", filters={"role": "Pharma Quality Manager"})
		
		if qa_managers:
			frappe.sendmail(
				recipients=[qa.email for qa in qa_managers],
				subject=f"SOP Review Due: {sop.sop_title}",
				message=f"""
				Dear QA Manager,
				
				The following SOP is due for review:
				
				SOP Number: {sop.sop_number}
				SOP Title: {sop.sop_title}
				Review Date: {sop.review_date}
				
				Please initiate the review process.
				
				Regards,
				Quality Management System
				""",
				reference_doctype="SOP Management",
				reference_name=sop.name
			)
	
	return {"success": True, "sops_reviewed": len(sops_due)}
