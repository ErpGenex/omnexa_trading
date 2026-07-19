# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today
from omnexa_trading.tests.test_helpers import (
	build_test_van_sales_invoice,
	create_test_customer,
	create_test_item,
	ensure_test_branch,
	ensure_test_company,
	ensure_test_customer_profile,
	ensure_test_employee,
	ensure_test_sales_representative,
	ensure_test_warehouse,
	inspector_link,
	item_link,
	cleanup_doc,
)

class TestPharmaEndToEnd(FrappeTestCase):
	def setUp(self):
		self.company = ensure_test_company()
		self.warehouse = ensure_test_warehouse(self.company.name)
		self.item = create_test_item(self.company.name)
		self.customer = create_test_customer(self.company.name)
		self.branch = ensure_test_branch(self.company.name)
		self.customer_profile = ensure_test_customer_profile(
			self.company.name, self.branch.name, self.customer
		)
		self.sales_rep = ensure_test_sales_representative(self.company.name, self.branch.name)
		self.inspector = ensure_test_employee(self.company.name)
	
	def test_complete_pharma_workflow(self):
		"""Test complete pharmaceutical workflow from batch to sale"""
		day = now_datetime().strftime("%Y%m%d")
		# Step 1: Create batch
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"E2E-BATCH-{day}",
			"item_code": item_link(self.item),
			"item_name": self.item.item_name,
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Pending",
			"is_active": 1
		})
		batch.insert()
		batch.submit()
		
		# Step 2: Create quality inspection
		inspection = frappe.get_doc({
			"doctype": "Pharma Quality Inspection",
			"inspection_number": f"E2E-QI-{day}",
			"inspection_date": today(),
			"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
			"item_code": item_link(self.item),
			"batch_number": batch.name,
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"overall_score": 90,
			"passing_score": 80
		})
		inspection.insert()
		inspection.submit()
		
		# Step 3: Verify batch approved
		batch.reload()
		self.assertEqual(batch.quality_status, "Approved")
		
		# Step 4: Create sales invoice
		invoice = build_test_van_sales_invoice(
			self.company.name,
			self.branch.name,
			self.customer_profile,
			self.sales_rep,
			[{
				"item_code": item_link(self.item),
				"qty": 10,
				"rate": 100,
				"batch_no": batch.batch_number,
			}],
		)
		invoice.insert()
		invoice.submit()
		
		# Step 5: Verify audit trail
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import get_audit_trail
		audit_logs = get_audit_trail("Trading Van Sales Invoice", invoice.name)
		self.assertGreater(len(audit_logs), 0)
		
		# Clean up
		cleanup_doc(invoice)
		cleanup_doc(inspection)
		cleanup_doc(batch)
	
	def test_controlled_substance_complete_workflow(self):
		"""Test complete controlled substance workflow"""
		day = now_datetime().strftime("%Y%m%d")
		controlled_batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"E2E-CTRL-{day}",
			"item_code": item_link(self.item),
			"item_name": self.item.item_name,
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Approved",
			"is_active": 1,
		})
		controlled_batch.insert()
		controlled_batch.submit()
		
		from omnexa_trading.omnexa_trading.doctype.pharma_regulatory_approval.pharma_regulatory_approval import create_regulatory_approval
		approval_name = create_regulatory_approval(
			controlled_batch.name,
			"Narcotic",
			"E2E-LICENSE-001",
			add_days(today(), 365)
		)
		
		approval = frappe.get_doc("Pharma Regulatory Approval", approval_name)
		approval.submit()
		
		frappe.db.set_value(
			"Pharma Batch",
			controlled_batch.name,
			{
				"controlled_substance_flag": 1,
				"license_number": "E2E-LICENSE-001",
				"license_expiry": add_days(today(), 365),
				"regulatory_approval": approval_name,
			},
		)
		controlled_batch.reload()
		
		# Step 3: Create sales invoice with prescription
		invoice = build_test_van_sales_invoice(
			self.company.name,
			self.branch.name,
			self.customer_profile,
			self.sales_rep,
			[{
				"item_code": item_link(self.item),
				"qty": 10,
				"rate": 100,
				"batch_no": controlled_batch.batch_number,
			}],
			prescription_number="E2E-RX-001",
		)
		invoice.insert()
		invoice.submit()
		
		# Step 4: Verify sale completed
		self.assertEqual(invoice.docstatus, 1)
		
		# Clean up
		cleanup_doc(invoice)
		cleanup_doc(approval)
		cleanup_doc(controlled_batch)
	
	def test_cold_chain_complete_workflow(self):
		"""Test complete cold chain workflow"""
		day = now_datetime().strftime("%Y%m%d")
		# Step 1: Create cold chain batch
		cold_chain_batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"E2E-COLD-{day}",
			"item_code": item_link(self.item),
			"item_name": self.item.item_name,
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Approved",
			"is_active": 1,
			"cold_chain_required": 1,
			"storage_temperature": "Refrigerated (2-8°C)"
		})
		cold_chain_batch.insert()
		cold_chain_batch.submit()
		
		# Step 2: Create temperature log
		temp_log = frappe.get_doc({
			"doctype": "Temperature Log",
			"log_number": f"E2E-TEMP-{day}",
			"log_date": today(),
			"batch_number": cold_chain_batch.name,
			"item_code": item_link(self.item),
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"temperature": 5,
			"temperature_unit": "°C",
			"min_temperature": 2,
			"max_temperature": 8
		})
		temp_log.insert()
		temp_log.submit()
		
		# Step 3: Verify temperature status
		self.assertEqual(temp_log.temperature_status, "Normal")
		self.assertEqual(temp_log.excursion_flag, 0)
		
		# Step 4: Get temperature summary
		from omnexa_trading.omnexa_trading.doctype.temperature_log.temperature_log import get_temperature_summary
		summary = get_temperature_summary(cold_chain_batch.name)
		self.assertIsNotNone(summary)
		
		# Clean up
		cleanup_doc(temp_log)
		cleanup_doc(cold_chain_batch)
	
	def test_product_recall_complete_workflow(self):
		"""Test complete product recall workflow"""
		day = now_datetime().strftime("%Y%m%d")
		# Step 1: Create batch
		recall_batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"E2E-RECALL-{day}",
			"item_code": item_link(self.item),
			"item_name": self.item.item_name,
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Approved",
			"is_active": 1
		})
		recall_batch.insert()
		recall_batch.submit()
		
		# Step 2: Create product recall
		from omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall import initiate_product_recall
		recall_name = initiate_product_recall(
			recall_batch.name,
			"Quality Issue",
			"Voluntary",
			"Class II (Serious Health Risk)"
		)
		
		recall = frappe.get_doc("Pharma Product Recall", recall_name)
		recall.submit()
		
		# Step 3: Verify batch quarantined
		recall_batch.reload()
		self.assertEqual(recall_batch.quality_status, "Quarantined")
		
		# Step 4: Notify customers
		from omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall import notify_customers
		notify_customers(recall_name)
		
		# Step 5: Complete recall
		from omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall import complete_recall
		complete_recall(
			recall_name,
			"Return and destroy affected products",
		 "Implement additional quality checks"
		)
		
		# Clean up
		cleanup_doc(recall)
		cleanup_doc(recall_batch)
	
	def test_field_level_security_workflow(self):
		"""Test field level security workflow"""
		# Step 1: Create field permission
		field_perm = frappe.new_doc("Field Permission")
		field_perm.permission_name = "E2E-FIELD-PERM"
		field_perm.target_doctype = "Pharma Batch"
		field_perm.field_name = "quality_status"
		field_perm.role = "System Manager"
		field_perm.mask_permission = 1
		field_perm.status = "Active"
		field_perm.insert()
		
		# Step 2: Test field permission check
		from omnexa_trading.omnexa_trading.doctype.field_permission.field_permission import check_field_permission
		permissions = check_field_permission("Pharma Batch", "quality_status")
		self.assertIn("mask", permissions)
		
		# Step 3: Test data masking
		from omnexa_trading.omnexa_trading.doctype.field_permission.field_permission import mask_field_value
		masked_value = mask_field_value("Pharma Batch", "quality_status", "Approved")
		self.assertIsNotNone(masked_value)
	
	def test_encryption_workflow(self):
		"""Test encryption workflow"""
		# Step 1: Create encryption key
		from omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key import generate_encryption_key
		key_value = generate_encryption_key("Fernet", 256)
		
		encryption_key = frappe.get_doc({
			"doctype": "Encryption Key",
			"key_name": "E2E-KEY",
			"key_type": "Symmetric",
			"algorithm": "Fernet",
			"key_length": 256,
			"key_value": key_value,
			"company": self.company.name,
			"status": "Active",
			"active": 1
		})
		encryption_key.insert()
		
		# Step 2: Test encryption
		from omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key import encrypt_data, decrypt_data
		test_data = "Sensitive Data"
		encrypted = encrypt_data(test_data, encryption_key.key_name)
		self.assertIsNotNone(encrypted)
		
		# Step 3: Test decryption
		decrypted = decrypt_data(encrypted, encryption_key.key_name)
		self.assertEqual(decrypted, test_data)
	
	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()
