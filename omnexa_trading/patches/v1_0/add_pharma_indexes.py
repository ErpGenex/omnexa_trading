# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""Add database indexes for pharmaceutical compliance features"""
	
	# Pharma Batch indexes
	if not frappe.db.has_index('Pharma Batch', 'expiry_date'):
		frappe.db.add_index('Pharma Batch', ['expiry_date'])
	
	if not frappe.db.has_index('Pharma Batch', 'quality_status'):
		frappe.db.add_index('Pharma Batch', ['quality_status'])
	
	if not frappe.db.has_index('Pharma Batch', 'item_code'):
		frappe.db.add_index('Pharma Batch', ['item_code'])
	
	if not frappe.db.has_index('Pharma Batch', 'is_active'):
		frappe.db.add_index('Pharma Batch', ['is_active'])
	
	if not frappe.db.has_index('Pharma Batch', 'batch_number'):
		frappe.db.add_index('Pharma Batch', ['batch_number'])
	
	# Pharma Quality Inspection indexes
	if not frappe.db.has_index('Pharma Quality Inspection', 'batch_number'):
		frappe.db.add_index('Pharma Quality Inspection', ['batch_number'])
	
	if not frappe.db.has_index('Pharma Quality Inspection', 'inspection_status'):
		frappe.db.add_index('Pharma Quality Inspection', ['inspection_status'])
	
	if not frappe.db.has_index('Pharma Quality Inspection', 'inspection_date'):
		frappe.db.add_index('Pharma Quality Inspection', ['inspection_date'])
	
	if not frappe.db.has_index('Pharma Quality Inspection', 'item_code'):
		frappe.db.add_index('Pharma Quality Inspection', ['item_code'])
	
	# Temperature Log indexes
	if not frappe.db.has_index('Temperature Log', 'batch_number'):
		frappe.db.add_index('Temperature Log', ['batch_number'])
	
	if not frappe.db.has_index('Temperature Log', 'log_date'):
		frappe.db.add_index('Temperature Log', ['log_date'])
	
	if not frappe.db.has_index('Temperature Log', 'temperature_status'):
		frappe.db.add_index('Temperature Log', ['temperature_status'])
	
	if not frappe.db.has_index('Temperature Log', 'excursion_flag'):
		frappe.db.add_index('Temperature Log', ['excursion_flag'])
	
	# Temperature Excursion indexes
	if not frappe.db.has_index('Temperature Excursion', 'batch_number'):
		frappe.db.add_index('Temperature Excursion', ['batch_number'])
	
	if not frappe.db.has_index('Temperature Excursion', 'resolution_status'):
		frappe.db.add_index('Temperature Excursion', ['resolution_status'])
	
	if not frappe.db.has_index('Temperature Excursion', 'excursion_date'):
		frappe.db.add_index('Temperature Excursion', ['excursion_date'])
	
	# Pharma Regulatory Approval indexes
	if not frappe.db.has_index('Pharma Regulatory Approval', 'batch_number'):
		frappe.db.add_index('Pharma Regulatory Approval', ['batch_number'])
	
	if not frappe.db.has_index('Pharma Regulatory Approval', 'approval_status'):
		frappe.db.add_index('Pharma Regulatory Approval', ['approval_status'])
	
	if not frappe.db.has_index('Pharma Regulatory Approval', 'license_expiry'):
		frappe.db.add_index('Pharma Regulatory Approval', ['license_expiry'])
	
	# Pharma Product Recall indexes
	if not frappe.db.has_index('Pharma Product Recall', 'batch_number'):
		frappe.db.add_index('Pharma Product Recall', ['batch_number'])
	
	if not frappe.db.has_index('Pharma Product Recall', 'recall_status'):
		frappe.db.add_index('Pharma Product Recall', ['recall_status'])
	
	if not frappe.db.has_index('Pharma Product Recall', 'recall_date'):
		frappe.db.add_index('Pharma Product Recall', ['recall_date'])
	
	if not frappe.db.has_index('Pharma Product Recall', 'severity'):
		frappe.db.add_index('Pharma Product Recall', ['severity'])
	
	# Audit Log indexes
	if not frappe.db.has_index('Audit Log', 'document_type'):
		frappe.db.add_index('Audit Log', ['document_type'])
	
	if not frappe.db.has_index('Audit Log', 'document_name'):
		frappe.db.add_index('Audit Log', ['document_name'])
	
	if not frappe.db.has_index('Audit Log', 'user'):
		frappe.db.add_index('Audit Log', ['user'])
	
	if not frappe.db.has_index('Audit Log', 'timestamp'):
		frappe.db.add_index('Audit Log', ['timestamp'])
	
	if not frappe.db.has_index('Audit Log', 'action'):
		frappe.db.add_index('Audit Log', ['action'])
	
	# Field Permission indexes
	if not frappe.db.has_index('Field Permission', 'doctype'):
		frappe.db.add_index('Field Permission', ['doctype'])
	
	if not frappe.db.has_index('Field Permission', 'field_name'):
		frappe.db.add_index('Field Permission', ['field_name'])
	
	if not frappe.db.has_index('Field Permission', 'role'):
		frappe.db.add_index('Field Permission', ['role'])
	
	if not frappe.db.has_index('Field Permission', 'status'):
		frappe.db.add_index('Field Permission', ['status'])
	
	# Encryption Key indexes
	if not frappe.db.has_index('Encryption Key', 'key_name'):
		frappe.db.add_index('Encryption Key', ['key_name'])
	
	if not frappe.db.has_index('Encryption Key', 'status'):
		frappe.db.add_index('Encryption Key', ['status'])
	
	if not frappe.db.has_index('Encryption Key', 'active'):
		frappe.db.add_index('Encryption Key', ['active'])
	
	if not frappe.db.has_index('Encryption Key', 'expiry_date'):
		frappe.db.add_index('Encryption Key', ['expiry_date'])
	
	# Composite indexes for common queries
	if not frappe.db.has_index('Pharma Batch', ['item_code', 'quality_status']):
		frappe.db.add_index('Pharma Batch', ['item_code', 'quality_status'])
	
	if not frappe.db.has_index('Pharma Batch', ['expiry_date', 'is_active']):
		frappe.db.add_index('Pharma Batch', ['expiry_date', 'is_active'])
	
	if not frappe.db.has_index('Audit Log', ['document_type', 'document_name']):
		frappe.db.add_index('Audit Log', ['document_type', 'document_name'])
	
	if not frappe.db.has_index('Audit Log', ['timestamp', 'user']):
		frappe.db.add_index('Audit Log', ['timestamp', 'user'])
	
	frappe.db.commit()
