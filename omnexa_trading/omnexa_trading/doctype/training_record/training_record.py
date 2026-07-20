# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, now
from frappe.model.document import Document

class TrainingRecord(Document):
	def validate(self):
		self._validate_training_dates()
		self._validate_instructor()
		self._validate_participants()
		self._generate_training_number()
		self._update_completion_rate()
	
	def before_save(self):
		self._set_prepared_date()
	
	def on_submit(self):
		self._validate_approvals()
		self._update_training_status()
		self._issue_certificates()
		self._log_submission()
	
	def on_cancel(self):
		self._update_training_status()
		self._log_cancellation()
	
	def _validate_training_dates(self):
		"""Validate training dates"""
		if self.training_date and getdate(self.training_date) < getdate():
			frappe.throw(_("Backdated training is not allowed"))
	
	def _validate_instructor(self):
		"""Validate instructor assignment"""
		if not self.instructor_name:
			frappe.throw(_("Instructor is required"))
	
	def _validate_participants(self):
		"""Validate participants"""
		if not self.training_participants:
			frappe.throw(_("At least one participant is required"))
		
		if self.max_participants and len(self.training_participants) > self.max_participants:
			frappe.throw(_("Number of participants exceeds maximum allowed"))
		
		if self.min_participants and len(self.training_participants) < self.min_participants:
			frappe.throw(_("Number of participants is below minimum required"))
	
	def _generate_training_number(self):
		"""Generate unique training number"""
		if not self.training_number:
			# Generate training number based on category and sequence
			category_code = {
				"GMP": "GMP",
				"GDP": "GDP",
				"Quality Control": "QC",
				"Safety": "SFT",
				"Compliance": "CMP",
				"Technical": "TEC",
				"Soft Skills": "SSK",
				"Management": "MGT",
				"Onboarding": "ONB"
			}
			
			code = category_code.get(self.training_category, "TRN")
			year = getdate().year
			sequence = frappe.db.count("Training Record", {
				"training_category": self.training_category,
				"training_date": [">=", getdate().replace(month=1, day=1)]
			}) + 1
			
			self.training_number = f"TRN-{code}-{year}-{sequence:04d}"
	
	def _update_completion_rate(self):
		"""Update completion rate based on participants"""
		if self.training_participants:
			completed = len([p for p in self.training_participants if p.attendance_status == "Completed"])
			self.completion_rate = (completed / len(self.training_participants)) * 100 if self.training_participants else 0
	
	def _set_prepared_date(self):
		"""Set prepared date if not set"""
		if not self.prepared_date and self.prepared_by:
			self.prepared_date = getdate()
	
	def _validate_approvals(self):
		"""Validate that required approvals are in place"""
		if not self.prepared_by or not self.prepared_date:
			frappe.throw(_("Training must be prepared and dated before submission"))
		
		if not self.instructor_name:
			frappe.throw(_("Instructor is required"))
	
	def _update_training_status(self):
		"""Update training status based on workflow"""
		if self.docstatus == 1:
			self.training_status = "Completed"
		elif self.docstatus == 2:
			self.training_status = "Cancelled"
	
	def _issue_certificates(self):
		"""Issue certificates to qualified participants"""
		if self.certificate_issued and self.training_status == "Completed":
			for participant in self.training_participants:
				if participant.assessment_score and participant.assessment_score >= (self.passing_score or 70):
					# Generate certificate number
					cert_num = f"CERT-{self.training_number}-{participant.employee}"
					participant.certificate_number = cert_num
					participant.certificate_issued = 1
					participant.certificate_date = getdate()
	
	def _log_submission(self):
		"""Log training submission to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Complete",
			document_type="Training Record",
			document_name=self.name,
			change_reason=f"Training {self.training_number} - {self.training_title} completed"
		)
	
	def _log_cancellation(self):
		"""Log training cancellation to audit trail"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_audit_event(
			action="Cancel",
			document_type="Training Record",
			document_name=self.name,
			change_reason=f"Training {self.training_number} - {self.training_title} cancelled"
		)

@frappe.whitelist()
def record_attendance(training_name, participant_list):
	"""
	Record attendance for training participants
	
	Parameters:
	- training_name: Name of training record
	- participant_list: List of participant attendance data
	
	Returns:
	- Success status
	"""
	training = frappe.get_doc("Training Record", training_name)
	
	for participant_data in participant_list:
		for participant in training.training_participants:
			if participant.employee == participant_data["employee"]:
				participant.attendance_status = participant_data["attendance_status"]
				participant.attendance_date = getdate()
				break
	
	training.save()
	
	return {"success": True, "message": "Attendance recorded successfully"
	}

@frappe.whitelist()
def record_assessment_results(training_name, assessment_results):
	"""
	Record assessment results for training participants
	
	Parameters:
	- training_name: Name of training record
	- assessment_results: List of assessment results
	
	Returns:
	- Success status
	"""
	training = frappe.get_doc("Training Record", training_name)
	
	for result in assessment_results:
		for participant in training.training_participants:
			if participant.employee == result["employee"]:
				participant.assessment_score = result["score"]
				participant.assessment_status = "Passed" if result["score"] >= (training.passing_score or 70) else "Failed"
				participant.assessment_date = getdate()
				break
	
	training.save()
	
	return {"success": True, "message": "Assessment results recorded successfully"
	}

@frappe.whitelist()
def get_training_summary(category=None, status=None):
	"""
	Get summary of training records
	
	Parameters:
	- category: Filter by category (optional)
	- status: Filter by status (optional)
	
	Returns:
	- Summary statistics
	"""
	filters = {}
	if category:
		filters["training_category"] = category
	if status:
		filters["training_status"] = status
	
	trainings = frappe.get_all("Training Record",
		filters=filters,
		fields=["name", "training_number", "training_title", "training_category", 
		       "training_status", "training_date", "completion_rate"]
	)
	
	summary = {
		"total": len(trainings),
		"by_status": {
	},
		"by_category": {
	},
		"average_completion": 0,
		"upcoming_trainings": []
	}
	
	today_date = getdate()
	thirty_days = add_days(today_date, 30)
	
	if trainings:
		for training in trainings:
			# Count by status
			summary["by_status"][training.training_status] = summary["by_status"].get(training.training_status, 0) + 1
			
			# Count by category
			summary["by_category"][training.training_category] = summary["by_category"].get(training.training_category, 0) + 1
			
			# Check upcoming trainings
			if training.training_date and training.training_date > today_date and training.training_date <= thirty_days:
				summary["upcoming_trainings"].append({
					"training_number": training.training_number,
					"training_title": training.training_title,
					"training_date": training.training_date
				})
		
		# Calculate average completion
		total_completion = sum(t.completion_rate for t in trainings)
		summary["average_completion"] = total_completion / len(trainings)
	
	return summary

@frappe.whitelist()
def get_competency_matrix(employee=None):
	"""
	Get competency matrix for employees
	
	Parameters:
	- employee: Filter by employee (optional)
	
	Returns:
	- Competency matrix
	"""
	filters = {}
	if employee:
		filters["employee"] = employee
	
	# Get all training participants
	participants = frappe.get_all("Training Participant",
		filters=filters,
		fields=["employee", "employee_name", "parent", "attendance_status", 
		       "assessment_score", "assessment_status", "certificate_number"]
	)
	
	competency_matrix = {}
	
	for participant in participants:
		training = frappe.get_doc("Training Record", participant.parent)
		
		if participant.employee not in competency_matrix:
			competency_matrix[participant.employee] = {
				"employee_name": participant.employee_name,
				"trainings": [],
				"total_trainings": 0,
				"completed_trainings": 0,
				"certified_trainings": 0
			}
		
		competency_matrix[participant.employee]["trainings"].append({
			"training_title": training.training_title,
			"training_category": training.training_category,
			"attendance_status": participant.attendance_status,
			"assessment_score": participant.assessment_score,
			"assessment_status": participant.assessment_status,
			"certificate_number": participant.certificate_number
		})
		
		competency_matrix[participant.employee]["total_trainings"] += 1
		
		if participant.attendance_status == "Completed":
			competency_matrix[participant.employee]["completed_trainings"] += 1
		
		if participant.certificate_number:
			competency_matrix[participant.employee]["certified_trainings"] += 1
	
	return competency_matrix

@frappe.whitelist()
def identify_training_gaps(employee=None, category=None):
	"""
	Identify training gaps for employees
	
	Parameters:
	- employee: Filter by employee (optional)
	- category: Filter by category (optional)
	
	Returns:
	- Training gaps
	"""
	# Define required training by role/department
	required_training = {
		"Pharma Warehouse Manager": ["GMP", "GDP", "Safety", "Quality Control"],
		"Pharma Quality Manager": ["GMP", "GDP", "Quality Control", "Compliance", "Management"],
		"Pharma Sales Representative": ["GMP", "GDP", "Compliance", "Soft Skills"],
		"Pharma Regulatory Officer": ["GMP", "GDP", "Compliance", "Quality Control"],
		"Pharma Cold Chain Manager": ["GMP", "GDP", "Cold Chain", "Safety"],
		"Pharma Finance Manager": ["GMP", "GDP", "Compliance", "Management"]
	}
	
	gaps = []
	
	if employee:
		employee_doc = frappe.get_doc("Employee", employee)
		employee_roles = [role.role for role in employee_doc.get("roles", [])]
		
		for role in employee_roles:
			if role in required_training:
				for required_category in required_training[role]:
					# Check if employee has completed this training
					has_training = frappe.db.exists("Training Participant", {
						"employee": employee,
						"attendance_status": "Completed"
					})
					
					if not has_training:
						gaps.append({
							"employee": employee,
							"role": role,
							"required_category": required_category,
							"status": "Not Completed"
						})
	
	return gaps

@frappe.whitelist()
def schedule_training_reminder():
	"""
	Send reminders for upcoming training
	Can be called as a scheduled task
	"""
	tomorrow = add_days(getdate(), 1)
	
	upcoming_trainings = frappe.get_all("Training Record",
		filters={
			"training_status": "Scheduled",
			"training_date": tomorrow
		},
		fields=["name", "training_number", "training_title", "training_date", "training_location"]
	)
	
	for training in upcoming_trainings:
		# Get participants
		participants = frappe.get_all("Training Participant",
			filters={"parent": training.name
	},
			fields=["employee", "employee_name"]
		)
		
		for participant in participants:
			employee = frappe.get_doc("Employee", participant.employee)
			if employee.user_id:
				frappe.sendmail(
					recipients=[employee.user_id],
					subject=f"Training Reminder: {training.training_title}",
					message=f"""
					Dear {participant.employee_name},
					
					This is a reminder that you have a training session scheduled for tomorrow:
					
					Training: {training.training_title}
					Date: {training.training_date}
					Location: {training.training_location}
					
					Please ensure you attend on time.
					
					Regards,
					Training Department
					""",
					reference_doctype="Training Record",
					reference_name=training.name
				)
	
	return {"success": True, "reminders_sent": len(upcoming_trainings)
	}
