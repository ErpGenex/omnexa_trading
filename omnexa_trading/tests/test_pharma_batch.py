# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today
from omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch import PharmaBatch
from omnexa_trading.tests.test_helpers import (
	create_test_item,
	ensure_test_company,
	ensure_test_warehouse,
	item_link,
	cleanup_doc,
)

class TestPharmaBatch(FrappeTestCase):
	def setUp(self):
		self.company = ensure_test_company()
		self.warehouse = ensure_test_warehouse(self.company.name)
		self.item = create_test_item(self.company.name)
	
	def test_batch_creation(self):
		"""Test batch creation"""
		batch_day = now_datetime().strftime("%Y%m%d")
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-BATCH-{batch_day
	}",
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
		
		self.assertEqual(batch.docstatus, 1)
		self.assertEqual(batch.quality_status, "Pending")
		self.assertEqual(batch.is_active, 1)
		
		cleanup_doc(batch)
	
	def test_batch_validation(self):
		"""Test batch validation"""
		# Test expiry date before manufacturing date
		batch_day = now_datetime().strftime("%Y%m%d")
		with self.assertRaises((frappe.ValidationError, frappe.DuplicateEntryError)):
			batch = frappe.get_doc({
				"doctype": "Pharma Batch",
				"batch_number": f"TEST-BATCH-INVALID-{batch_day
	}",
				"item_code": item_link(self.item),
				"manufacturing_date": add_days(today(), 10),
				"expiry_date": today(),
				"batch_size": 100,
			"uom": "Nos",
				"warehouse": self.warehouse.name,
				"company": self.company.name
			})
			batch.insert()
	
	def test_batch_uniqueness(self):
		"""Test batch number uniqueness"""
		batch_number = f"TEST-BATCH-DUPLICATE-{now_datetime().strftime('%Y%m%d%H%M%S')}"
		
		# Create first batch
		batch1 = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": batch_number,
			"item_code": item_link(self.item),
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name
		})
		batch1.insert()
		
		# Try to create duplicate batch
		with self.assertRaises((frappe.ValidationError, frappe.DuplicateEntryError)):
			batch2 = frappe.get_doc({
				"doctype": "Pharma Batch",
				"batch_number": batch_number,
				"item_code": item_link(self.item),
				"manufacturing_date": today(),
				"expiry_date": add_days(today(), 365),
				"batch_size": 100,
			"uom": "Nos",
				"warehouse": self.warehouse.name,
				"company": self.company.name
			})
			batch2.insert()
		
		cleanup_doc(batch1)
	
	def test_batch_expiry_calculation(self):
		"""Test batch expiry calculation"""
		expiry_date = add_days(today(), 30)
		
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-BATCH-EXPIRY-{now_datetime().strftime('%Y%m%d%H%M%S')
	}",
			"item_code": item_link(self.item),
			"manufacturing_date": today(),
			"expiry_date": expiry_date,
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name
		})
		batch.insert()
		
		self.assertEqual(batch.days_until_expiry, 30)
		
		cleanup_doc(batch)
	
	def test_batch_quality_status(self):
		"""Test batch quality status"""
		batch = frappe.get_doc({
			"doctype": "Pharma Batch",
			"batch_number": f"TEST-BATCH-QUALITY-{now_datetime().strftime('%Y%m%d%H%M%S')
	}",
			"item_code": item_link(self.item),
			"manufacturing_date": today(),
			"expiry_date": add_days(today(), 365),
			"batch_size": 100,
			"uom": "Nos",
			"warehouse": self.warehouse.name,
			"company": self.company.name,
			"quality_status": "Approved"
		})
		batch.insert()
		
		self.assertEqual(batch.quality_status, "Approved")
		
		cleanup_doc(batch)
	
	def tearDown(self):
		# Clean up test data
		frappe.db.rollback()
