# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, now_datetime
from frappe.model.naming import make_autoname
import json

class AuditLog(Document):
	def validate(self):
		self._validate_log_id()
		self._set_timestamp_if_missing()

	def _validate_log_id(self):
		"""Validate log ID is unique"""
		if not self.log_id:
			self.log_id = make_autoname("AUDIT-LOG-.####")
		
		if frappe.db.exists("Audit Log", {
			"log_id": self.log_id,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Log ID {0} already exists").format(self.log_id))

	def _set_timestamp_if_missing(self):
		"""Set timestamp if missing"""
		if not self.timestamp:
			self.timestamp = now()

@frappe.whitelist()
def log_audit_event(action, document_type, document_name, field_changes=None, old_value=None, new_value=None, change_reason=None):
	"""
	Log an audit event
	
	Parameters:
	- action: Create, Update, Delete, Submit, Cancel, Read, Export, Import
	- document_type: DocType name
	- document_name: Document name/ID
	- field_changes: List of field changes (optional)
	- old_value: Old value of the document (optional)
	- new_value: New value of the document (optional)
	- change_reason: Reason for the change (optional)
	"""
	try:
		audit_log = frappe.new_doc("Audit Log")
		audit_log.log_id = f"AUDIT-{action}-{document_type}-{document_name}-{now_datetime().strftime('%Y%m%d%H%M%S')}"
		audit_log.timestamp = now()
		audit_log.user = frappe.session.user
		audit_log.action = action
		audit_log.document_type = document_type
		audit_log.document_name = document_name
		
		# Get IP address and user agent from request
		request = getattr(frappe.local, "request", None)
		if request:
			audit_log.ip_address = getattr(frappe.local, "request_ip", None)
			audit_log.user_agent = request.headers.get("User-Agent", "")
			audit_log.session_id = frappe.session.sid
		
		# Set company if available
		if frappe.db.exists(document_type, document_name):
			doc = frappe.get_doc(document_type, document_name)
			if hasattr(doc, "company"):
				audit_log.company = doc.company
		
		# Set field changes
		if field_changes:
			for change in field_changes:
				audit_log.append("field_changes", {
					"field_name": change.get("field_name"),
					"old_value": change.get("old_value"),
					"new_value": change.get("new_value")
				})
		
		# Set old and new values
		if old_value:
			audit_log.old_value = json.dumps(old_value, indent=2) if isinstance(old_value, (dict, list)) else str(old_value)
		if new_value:
			audit_log.new_value = json.dumps(new_value, indent=2) if isinstance(new_value, (dict, list)) else str(new_value)
		
		audit_log.change_reason = change_reason
		
		audit_log.insert()
		
		return audit_log.name
	except Exception as e:
		frappe.log_error(f"Failed to log audit event: {str(e)}", "Audit Log Error")
		return None

@frappe.whitelist()
def get_audit_trail(document_type, document_name):
	"""Get audit trail for a document"""
	logs = frappe.get_all("Audit Log", {
		"document_type": document_type,
		"document_name": document_name
	}, ["name", "log_id", "timestamp", "user", "action", "ip_address", "change_reason"],
		order_by="timestamp DESC")
	
	return logs

@frappe.whitelist()
def get_user_activity(user, from_date=None, to_date=None):
	"""Get user activity logs"""
	filters = {"user": user}
	
	if from_date:
		filters["timestamp"] = [">=", from_date]
	if to_date:
		if "timestamp" in filters:
			filters["timestamp"].append(["<=", to_date])
		else:
			filters["timestamp"] = ["<=", to_date]
	
	logs = frappe.get_all("Audit Log", filters, 
		["name", "log_id", "timestamp", "action", "document_type", "document_name", "ip_address"],
		order_by="timestamp DESC",
		limit=100)
	
	return logs

@frappe.whitelist()
def get_security_events(from_date=None, to_date=None, event_type=None):
	"""Get security events"""
	filters = {}
	
	if from_date:
		filters["timestamp"] = [">=", from_date]
	if to_date:
		if "timestamp" in filters:
			filters["timestamp"].append(["<=", to_date])
		else:
			filters["timestamp"] = ["<=", to_date]
	if event_type:
		filters["action"] = event_type
	
	logs = frappe.get_all("Audit Log", filters,
		["name", "log_id", "timestamp", "user", "action", "document_type", "document_name", "ip_address"],
		order_by="timestamp DESC",
		limit=100)
	
	return logs
