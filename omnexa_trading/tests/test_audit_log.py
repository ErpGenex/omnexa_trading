# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

class TestAuditLog(FrappeTestCase):
	def setUp(self):
		# Company autoname often uses `abbr` as document name.
		if not frappe.db.exists("Company", "TPC"):
			self.company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Pharma Company",
					"abbr": "TPC",
					"country": "United Arab Emirates",
					"default_currency": "AED"
	}
			).insert()
		else:
			self.company = frappe.get_doc("Company", "TPC")
	
	def test_audit_log_creation(self):
		"""Test audit log creation"""
		ts = now_datetime().strftime("%Y%m%d%H%M%S")
		log = frappe.get_doc({
			"doctype": "Audit Log",
			"log_id": f"AUDIT-{ts
	}",
			"timestamp": frappe.utils.now(),
			"user": frappe.session.user,
			"action": "Create",
			"document_type": "Pharma Batch",
			"document_name": "TEST-BATCH-001",
			"company": self.company.name
		})
		log.insert()
		
		self.assertEqual(log.action, "Create")
		self.assertEqual(log.document_type, "Pharma Batch")
		self.assertEqual(log.user, frappe.session.user)
	
	def test_audit_log_uniqueness(self):
		"""Test audit log ID uniqueness"""
		log_id = f"AUDIT-TEST-{now_datetime().strftime('%Y%m%d%H%M%S')}"
		
		# Create first log
		log1 = frappe.get_doc({
			"doctype": "Audit Log",
			"log_id": log_id,
			"timestamp": frappe.utils.now(),
			"user": frappe.session.user,
			"action": "Create",
			"document_type": "Pharma Batch",
			"document_name": "TEST-BATCH-001",
			"company": self.company.name
		})
		log1.insert()
		
		# Try to create duplicate log
		with self.assertRaises(frappe.ValidationError):
			log2 = frappe.get_doc({
				"doctype": "Audit Log",
				"log_id": log_id,
				"timestamp": frappe.utils.now(),
				"user": frappe.session.user,
				"action": "Update",
				"document_type": "Pharma Batch",
				"document_name": "TEST-BATCH-001",
				"company": self.company.name
			})
			log2.insert()
	
	def test_audit_log_field_changes(self):
		"""Test audit log field changes"""
		ts = now_datetime().strftime("%Y%m%d%H%M%S")
		log = frappe.get_doc({
			"doctype": "Audit Log",
			"log_id": f"AUDIT-FIELD-{ts
	}",
			"timestamp": frappe.utils.now(),
			"user": frappe.session.user,
			"action": "Update",
			"document_type": "Pharma Batch",
			"document_name": "TEST-BATCH-001",
			"company": self.company.name
		})
		
		# Add field changes
		log.append("field_changes", {
			"field_name": "quality_status",
			"old_value": "Pending",
			"new_value": "Approved"
		})
		log.append("field_changes", {
			"field_name": "is_active",
			"old_value": "0",
			"new_value": "1"
		})
		
		log.insert()
		
		self.assertEqual(len(log.field_changes), 2)
	
	def test_audit_log_api_function(self):
		"""Test audit log API function"""
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import log_audit_event
		
		log_name = log_audit_event(
			action="Create",
			document_type="Pharma Batch",
			document_name="TEST-BATCH-API",
			change_reason="Test API call"
		)
		
		self.assertIsNotNone(log_name)
		
		# Verify log was created
		log = frappe.get_doc("Audit Log", log_name)
		self.assertEqual(log.action, "Create")
		self.assertEqual(log.change_reason, "Test API call")
	
	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()
