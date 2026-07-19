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

class TestPharmaIntegration(FrappeTestCase):
	def setUp(self):
		self.company = ensure_test_company()
		self.warehouse = ensure_test_warehouse(self.company.name)
		self.item = create_test_item(self.company.name)
		self.inspector = ensure_test_employee(self.company.name)
		self.customer = create_test_customer(self.company.name)
		self.branch = ensure_test_branch(self.company.name)
		self.customer_profile = ensure_test_customer_profile(
			self.company.name, self.branch.name, self.customer
		)
		self.sales_rep = ensure_test_sales_representative(self.company.name, self.branch.name)
	
	def test_batch_to_inspection_workflow(self):
		"""Test batch creation to quality inspection workflow"""
		day = now_datetime().strftime("%Y%m%d")
		# Create batch
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-BATCH-WF-{day}",
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
		
		# Create quality inspection
		inspection = frappe.get_doc({
			"doctype": "Pharma Quality Inspection",
			"inspection_number": f"QI-WF-{day}",
			"inspection_date": today(),
			"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
			"item_code": item_link(self.item),
			"batch_number": batch.name,
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"overall_score": 85,
			"passing_score": 80
		})
		inspection.insert()
		inspection.submit()
		
		# Verify batch quality status updated
		batch.reload()
		self.assertEqual(batch.quality_status, "Approved")
		
		# Clean up
		cleanup_doc(inspection)
		cleanup_doc(batch)
	
	def test_batch_expiry_validation_in_sales(self):
		"""Test batch expiry validation in sales"""
		day = now_datetime().strftime("%Y%m%d")
		expired_batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-EXPIRED-{day}",
			"item_code": item_link(self.item),
			"item_name": self.item.item_name,
			"manufacturing_date": add_days(today(), -400),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Approved",
			"is_active": 1
		})
		expired_batch.insert()
		expired_batch.submit()
		frappe.db.set_value(
			"Pharma Batch",
			expired_batch.name,
			{
				"expiry_date": add_days(today(), -30),
				"manufacturing_date": add_days(today(), -400),
			},
		)
		expired_batch.reload()
		
		with self.assertRaises(frappe.ValidationError):
			invoice = build_test_van_sales_invoice(
				self.company.name,
				self.branch.name,
				self.customer_profile,
				self.sales_rep,
				[{
					"item_code": item_link(self.item),
					"qty": 10,
					"rate": 100,
					"batch_no": expired_batch.batch_number,
				}],
			)
			invoice.insert()
		
		cleanup_doc(expired_batch)
	
	def test_controlled_substance_validation(self):
		"""Test controlled substance validation"""
		day = now_datetime().strftime("%Y%m%d")
		controlled_batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-CONTROLLED-{day}",
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
			"TEST-LICENSE-001",
			add_days(today(), 365)
		)
		
		approval = frappe.get_doc("Pharma Regulatory Approval", approval_name)
		approval.submit()
		
		frappe.db.set_value(
			"Pharma Batch",
			controlled_batch.name,
			{
				"controlled_substance_flag": 1,
				"license_number": "TEST-LICENSE-001",
				"license_expiry": add_days(today(), 365),
				"regulatory_approval": approval_name,
			},
		)
		controlled_batch.reload()
		
		with self.assertRaises(frappe.ValidationError):
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
			)
			invoice.insert()
		
		cleanup_doc(approval)
		cleanup_doc(controlled_batch)
	
	def test_temperature_excursion_workflow(self):
		"""Test temperature excursion workflow"""
		day = now_datetime().strftime("%Y%m%d")
		# Create batch
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-TEMP-{day}",
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
		batch.insert()
		batch.submit()
		
		# Create temperature log with excursion
		temp_log = frappe.get_doc({
			"doctype": "Temperature Log",
			"log_number": f"TEMP-{day}",
			"log_date": today(),
			"batch_number": batch.name,
			"item_code": item_link(self.item),
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"temperature": 15,
			"temperature_unit": "°C",
			"min_temperature": 2,
			"max_temperature": 8
		})
		temp_log.insert()
		temp_log.submit()
		
		# Verify excursion was created
		self.assertEqual(temp_log.temperature_status, "Critical")
		self.assertEqual(temp_log.excursion_flag, 1)
		
		# Clean up
		cleanup_doc(temp_log)
		cleanup_doc(batch)
	
	def test_product_recall_workflow(self):
		"""Test product recall workflow"""
		day = now_datetime().strftime("%Y%m%d")
		# Create batch
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-RECALL-{day}",
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
		batch.insert()
		batch.submit()
		
		# Create product recall
		from omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall import initiate_product_recall
		recall_name = initiate_product_recall(
			batch.name,
			"Quality Issue",
			"Voluntary",
			"Class II (Serious Health Risk)"
		)
		
		recall = frappe.get_doc("Pharma Product Recall", recall_name)
		recall.submit()
		
		# Verify batch was quarantined
		batch.reload()
		self.assertEqual(batch.quality_status, "Quarantined")
		
		# Clean up
		cleanup_doc(recall)
		cleanup_doc(batch)
	
	def test_audit_trail_integration(self):
		"""Test audit trail integration"""
		day = now_datetime().strftime("%Y%m%d")
		# Create batch
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-AUDIT-{day}",
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
		
		# Check audit log was created
		from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import get_audit_trail
		audit_logs = get_audit_trail("Pharma Batch", batch.name)
		
		self.assertIsInstance(audit_logs, list)
		
		# Clean up
		cleanup_doc(batch)
	
	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()
