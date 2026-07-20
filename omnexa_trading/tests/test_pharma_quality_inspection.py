# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today
from omnexa_trading.tests.test_helpers import (
	create_test_item,
	ensure_test_company,
	ensure_test_employee,
	ensure_test_warehouse,
	inspector_link,
	item_link,
	cleanup_doc,
)

class TestPharmaQualityInspection(FrappeTestCase):
	def setUp(self):
		self.company = ensure_test_company()
		self.warehouse = ensure_test_warehouse(self.company.name)
		self.item = create_test_item(self.company.name)
		self.inspector = ensure_test_employee(self.company.name)

		batch_number = f"TEST-BATCH-QI-{now_datetime().strftime('%H%M%S%f')}"
		self.batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": batch_number,
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
		self.batch.insert()
	
	def test_quality_inspection_creation(self):
		"""Test quality inspection creation"""
		day = now_datetime().strftime("%Y%m%d")
		inspection = frappe.get_doc({
			"doctype": "Pharma Quality Inspection",
			"inspection_number": f"QI-{day
	}-001",
			"inspection_date": today(),
			"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
			"item_code": item_link(self.item),
			"batch_number": self.batch.name,
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"inspection_status": "Passed",
			"overall_score": 85,
			"passing_score": 80
		})
		inspection.insert()
		inspection.submit()
		
		self.assertEqual(inspection.docstatus, 1)
		self.assertEqual(inspection.inspection_status, "Passed")
		
		# Check batch quality status updated
		self.batch.reload()
		self.assertEqual(self.batch.quality_status, "Approved")
		
		cleanup_doc(inspection)
	
	def test_quality_inspection_validation(self):
		"""Test quality inspection validation"""
		# Test inspection without batch
		day = now_datetime().strftime("%Y%m%d")
		with self.assertRaises(frappe.ValidationError):
			inspection = frappe.get_doc({
				"doctype": "Pharma Quality Inspection",
				"inspection_number": f"QI-{day
	}-002",
				"inspection_date": today(),
				"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
				"item_code": item_link(self.item),
				"company": self.company.name
			})
			inspection.insert()
	
	def test_quality_inspection_score_calculation(self):
		"""Test quality inspection score calculation"""
		day = now_datetime().strftime("%Y%m%d")
		inspection = frappe.get_doc({
			"doctype": "Pharma Quality Inspection",
			"inspection_number": f"QI-{day
	}-003",
			"inspection_date": today(),
			"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
			"item_code": item_link(self.item),
			"batch_number": self.batch.name,
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"passing_score": 80
		})
		
		# Add quality parameters
		inspection.append("quality_parameters", {
			"parameter_name": "Appearance",
			"score": 90,
			"weight": 1
		})
		inspection.append("quality_parameters", {
			"parameter_name": "Purity",
			"score": 85,
			"weight": 1
		})
		
		inspection.insert()
		
		self.assertEqual(inspection.overall_score, 87.5)
		
		cleanup_doc(inspection)
	
	def test_quality_inspection_failed_status(self):
		"""Test quality inspection failed status"""
		day = now_datetime().strftime("%Y%m%d")
		inspection = frappe.get_doc({
			"doctype": "Pharma Quality Inspection",
			"inspection_number": f"QI-{day
	}-004",
			"inspection_date": today(),
			"inspection_type": "Incoming",
			"inspector": inspector_link(self.inspector),
			"item_code": item_link(self.item),
			"batch_number": self.batch.name,
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"overall_score": 75,
			"passing_score": 80
		})
		inspection.insert()
		
		self.assertEqual(inspection.inspection_status, "Failed")
		
		cleanup_doc(inspection)
	
	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()
