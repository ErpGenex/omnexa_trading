# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def log_document_create(doc, method=None):
	"""Log document creation"""
	try:
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		log_audit_event(
			action="Create",
			document_type=doc.doctype,
			document_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"Failed to log document create: {str(e)}", "Audit Log Error")

def log_document_update(doc, method=None):
	"""Log document update"""
	try:
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		log_audit_event(
			action="Update",
			document_type=doc.doctype,
			document_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"Failed to log document update: {str(e)}", "Audit Log Error")

def log_document_delete(doc, method=None):
	"""Log document deletion"""
	try:
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		log_audit_event(
			action="Delete",
			document_type=doc.doctype,
			document_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"Failed to log document delete: {str(e)}", "Audit Log Error")

def log_document_submit(doc, method=None):
	"""Log document submission"""
	try:
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		log_audit_event(
			action="Submit",
			document_type=doc.doctype,
			document_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"Failed to log document submit: {str(e)}", "Audit Log Error")

def log_document_cancel(doc, method=None):
	"""Log document cancellation"""
	try:
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		log_audit_event(
			action="Cancel",
			document_type=doc.doctype,
			document_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"Failed to log document cancel: {str(e)}", "Audit Log Error")
