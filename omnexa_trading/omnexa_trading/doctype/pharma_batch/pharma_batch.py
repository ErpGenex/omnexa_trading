# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	getdate,
	flt,
	nowdate,
	cint
)
from frappe.model.naming import make_autoname

class PharmaBatch(Document):
	def validate(self):
		self._validate_batch_number()
		self._validate_dates()
		self._validate_item()
		self._calculate_days_until_expiry()
		self._calculate_total_cost()
		self._populate_item_details()
		self._validate_quality_status()
		self._validate_expiry_date()
		self._check_controlled_substance()

	def on_submit(self):
		self._update_item_batch_tracking()
		self._create_stock_entry_if_needed()
		self._set_quality_status()
		self.db_set("status", "Approved")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def _validate_batch_number(self):
		"""Validate batch number is unique"""
		if not self.batch_number:
			self.batch_number = make_autoname("BATCH-.####")
		
		# Check for duplicate batch number
		if frappe.db.exists("Pharma Batch", {
			"batch_number": self.batch_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Batch Number {0} already exists").format(self.batch_number))

	def _validate_dates(self):
		"""Validate manufacturing and expiry dates"""
		if not self.manufacturing_date:
			frappe.throw(_("Manufacturing Date is required"))
		
		if not self.expiry_date:
			frappe.throw(_("Expiry Date is required"))
		
		if getdate(self.expiry_date) <= getdate(self.manufacturing_date):
			frappe.throw(_("Expiry Date must be after Manufacturing Date"))
		
		if getdate(self.expiry_date) < getdate():
			frappe.throw(_("Expiry Date cannot be in the past"))

	def _validate_item(self):
		"""Validate item and populate details"""
		if not self.item_code:
			frappe.throw(_("Item Code is required"))
		
		# Get item details
		item = frappe.get_doc("Item", self.item_code)
		self.item_name = item.item_name
		
		# Check if item is linked to Pharma Drug Registration
		if frappe.db.exists("Pharma Drug Registration", {"item_code": self.item_code}):
			drug = frappe.get_doc("Pharma Drug Registration", {"item_code": self.item_code})
			self.drug_code = drug.drug_code
			self.drug_name = drug.drug_name
			self.controlled_substance_flag = drug.is_controlled
			self.schedule_class = drug.schedule_class
			self.cold_chain_required = drug.cold_chain_required
			self.storage_temperature = drug.storage_temperature
			self.shelf_life_months = drug.shelf_life_months

	def _calculate_days_until_expiry(self):
		"""Calculate days until expiry"""
		if self.expiry_date:
			self.days_until_expiry = (getdate(self.expiry_date) - getdate()).days
			if self.days_until_expiry < 0:
				self.days_until_expiry = 0

	def _calculate_total_cost(self):
		"""Calculate total cost"""
		if self.batch_size and self.cost_per_unit:
			self.total_cost = flt(self.batch_size) * flt(self.cost_per_unit)

	def _populate_item_details(self):
		"""Populate item details from Item master"""
		if self.item_code:
			item = frappe.get_doc("Item", self.item_code)
			if not self.uom:
				self.uom = item.stock_uom
			if not self.batch_size:
				self.batch_size = 1
			if not self.cost_per_unit:
				self.cost_per_unit = flt(
					getattr(item, "standard_rate", None)
					or getattr(item, "valuation_rate", None)
					or getattr(item, "last_purchase_rate", None)
				)

	def _validate_quality_status(self):
		"""Validate quality status transitions"""
		if self.quality_status == "Quarantined" and not self.quarantine_reason:
			frappe.throw(_("Quarantine Reason is required when Quality Status is Quarantined"))
		
		if self.quality_status == "Quarantined" and not self.quarantine_date:
			self.quarantine_date = nowdate()
		
		if self.quality_status == "Approved" and not self.release_date:
			self.release_date = nowdate()

	def _validate_expiry_date(self):
		"""Validate expiry date against shelf life"""
		if self.shelf_life_months and self.manufacturing_date:
			expected_expiry = add_days(self.manufacturing_date, self.shelf_life_months * 30)
			if getdate(self.expiry_date) > getdate(expected_expiry):
				frappe.msgprint(_("Warning: Expiry Date exceeds expected shelf life"))

	def _check_controlled_substance(self):
		"""Check if controlled substance and validate requirements"""
		if self.controlled_substance_flag:
			if not self.license_number:
				frappe.throw(_("License Number is required for Controlled Substances"))
			
			if not self.license_expiry:
				frappe.throw(_("License Expiry is required for Controlled Substances"))
			
			if getdate(self.license_expiry) < getdate():
				frappe.throw(_("License has expired"))
			
			if not self.regulatory_approval:
				frappe.throw(_("Regulatory Approval is required for Controlled Substances"))

	def _update_item_batch_tracking(self):
		"""Update item to enable batch tracking"""
		if self.item_code:
			item = frappe.get_doc("Item", self.item_code)
			if hasattr(item, "has_batch_no") and not item.has_batch_no:
				item.has_batch_no = 1
				item.save()
				frappe.msgprint(_("Batch tracking enabled for Item {0}").format(self.item_code))

	def _create_stock_entry_if_needed(self):
		"""Create stock entry if batch size is provided"""
		if self.batch_size and self.warehouse:
			try:
				stock_entry = frappe.new_doc("Stock Entry")
				stock_entry.stock_entry_type = "Material Receipt"
				stock_entry.company = self.company
				stock_entry.set_warehouse = self.warehouse
				stock_entry.posting_date = nowdate()
				
				stock_entry.append("items", {
					"item_code": self.item_code,
					"item_name": self.item_name,
					"qty": self.batch_size,
					"uom": self.uom,
					"batch_no": self.batch_number,
					"warehouse": self.warehouse,
					"allow_zero_valuation_rate": 1
				})
				
				stock_entry.submit()
				frappe.msgprint(_("Stock Entry created for Batch {0}").format(self.batch_number))
			except Exception as e:
				frappe.msgprint(_("Could not create Stock Entry: {0}").format(str(e)))

	def _set_quality_status(self):
		"""Set quality status based on inspection"""
		if self.quality_inspection:
			inspection = frappe.get_doc("Pharma Quality Inspection", self.quality_inspection)
			if inspection.inspection_status == "Passed":
				self.quality_status = "Approved"
			elif inspection.inspection_status == "Failed":
				self.quality_status = "Rejected"
			elif inspection.inspection_status == "Hold":
				self.quality_status = "Quarantined"

@frappe.whitelist()
def get_batch_expiry_alerts():
	"""Get batches with near expiry or expired"""
	from datetime import datetime, timedelta
	
	today = getdate()
	near_expiry = today + timedelta(days=90)
	
	batches = frappe.get_all("Pharma Batch", {
		"expiry_date": ("<=", near_expiry),
		"is_active": 1,
		"quality_status": "Approved"
	}, ["name", "batch_number", "item_code", "expiry_date", "days_until_expiry"])
	
	alerts = []
	for batch in batches:
		batch_doc = frappe.get_doc("Pharma Batch", batch.name)
		if batch_doc.days_until_expiry <= 0:
			alert_type = "Expired"
		elif batch_doc.days_until_expiry <= 30:
			alert_type = "Critical"
		elif batch_doc.days_until_expiry <= 60:
			alert_type = "Warning"
		else:
			alert_type = "Near Expiry"
		
		alerts.append({
			"batch": batch.batch_number,
			"item": batch.item_code,
			"expiry_date": batch.expiry_date,
			"days_until_expiry": batch.days_until_expiry,
			"alert_type": alert_type
		})
	
	return alerts

@frappe.whitelist()
def get_batch_stock(batch_no):
	"""Get stock for a specific batch"""
	from frappe.query_builder import DocType, Query
	from frappe.query_builder.functions import Sum
	
	bin = DocType("Bin")
	
	query = (
		frappe.qb.from_(bin)
		.select(
			bin.item_code,
			bin.warehouse,
			Sum(bin.actual_qty).as_("qty")
		)
		.where(bin.batch_no == batch_no)
		.groupby(bin.item_code, bin.warehouse)
	)
	
	return query.run(as_dict=True)

@frappe.whitelist()
def validate_batch_for_sale(item_code, batch_no):
	"""Validate if batch can be sold"""
	batch = frappe.get_doc("Pharma Batch", {"batch_number": batch_no, "item_code": item_code})
	
	# Check if batch is active
	if not batch.is_active:
		return {"valid": False, "message": "Batch is not active"}
	
	# Check quality status
	if batch.quality_status != "Approved":
		return {"valid": False, "message": f"Batch quality status is {batch.quality_status}"}
	
	# Check if expired
	if batch.days_until_expiry <= 0:
		return {"valid": False, "message": "Batch has expired"}
	
	# Check if controlled substance and license valid
	if batch.controlled_substance_flag:
		if getdate(batch.license_expiry) < getdate():
			return {"valid": False, "message": "License has expired"}
	
	return {"valid": True, "message": "Batch is valid for sale"}

@frappe.whitelist()
def get_fefo_batches(item_code, warehouse=None, qty=1):
	"""
	Get batches for an item using FEFO (First Expired, First Out) logic
	
	Parameters:
	- item_code: Item code
	- warehouse: Warehouse (optional)
	- qty: Required quantity
	
	Returns:
	- List of batches sorted by expiry date (earliest first)
	"""
	from frappe.query_builder import DocType, Order
	from frappe.query_builder.functions import Sum
	
	batch = DocType("Pharma Batch")
	bin = DocType("Bin")
	
	query = (
		frappe.qb.from_(batch)
		.left_join(bin)
		.on(batch.batch_number == bin.batch_no)
		.select(
			batch.name,
			batch.batch_number,
			batch.item_code,
			batch.expiry_date,
			batch.days_until_expiry,
			batch.quality_status,
			batch.is_active,
			Sum(bin.actual_qty).as_("available_qty")
		)
		.where(batch.item_code == item_code)
		.where(batch.is_active == 1)
		.where(batch.quality_status == "Approved")
		.where(batch.days_until_expiry > 0)
	)
	
	if warehouse:
		query = query.where((bin.warehouse == warehouse) | (bin.warehouse.isnull()))
	
	query = query.orderby(batch.expiry_date, Order.asc)
	
	batches = query.run(as_dict=True)
	
	# Filter batches with available quantity
	available_batches = []
	for b in batches:
		if b.available_qty and b.available_qty > 0:
			available_batches.append(b)
	
	return available_batches

@frappe.whitelist()
def get_fifo_batches(item_code, warehouse=None, qty=1):
	"""
	Get batches for an item using FIFO (First In, First Out) logic
	
	Parameters:
	- item_code: Item code
	- warehouse: Warehouse (optional)
	- qty: Required quantity
	
	Returns:
	- List of batches sorted by manufacturing date (earliest first)
	"""
	from frappe.query_builder import DocType, Order
	from frappe.query_builder.functions import Sum
	
	batch = DocType("Pharma Batch")
	bin = DocType("Bin")
	
	query = (
		frappe.qb.from_(batch)
		.left_join(bin)
		.on(batch.batch_number == bin.batch_no)
		.select(
			batch.name,
			batch.batch_number,
			batch.item_code,
			batch.manufacturing_date,
			batch.expiry_date,
			batch.days_until_expiry,
			batch.quality_status,
			batch.is_active,
			Sum(bin.actual_qty).as_("available_qty")
		)
		.where(batch.item_code == item_code)
		.where(batch.is_active == 1)
		.where(batch.quality_status == "Approved")
		.where(batch.days_until_expiry > 0)
	)
	
	if warehouse:
		query = query.where((bin.warehouse == warehouse) | (bin.warehouse.isnull()))
	
	query = query.orderby(batch.manufacturing_date, Order.asc)
	
	batches = query.run(as_dict=True)
	
	# Filter batches with available quantity
	available_batches = []
	for b in batches:
		if b.available_qty and b.available_qty > 0:
			available_batches.append(b)
	
	return available_batches

@frappe.whitelist()
def suggest_batch_for_picking(item_code, warehouse=None, qty=1, picking_strategy="FEFO"):
	"""
	Suggest batch for picking based on strategy
	
	Parameters:
	- item_code: Item code
	- warehouse: Warehouse (optional)
	- qty: Required quantity
	- picking_strategy: FEFO or FIFO
	
	Returns:
	- Suggested batch with available quantity
	"""
	if picking_strategy == "FEFO":
		batches = get_fefo_batches(item_code, warehouse, qty)
	elif picking_strategy == "FIFO":
		batches = get_fifo_batches(item_code, warehouse, qty)
	else:
		batches = get_fefo_batches(item_code, warehouse, qty)
	
	if not batches:
		return None
	
	# Find batch with sufficient quantity
	for batch in batches:
		if batch.available_qty >= qty:
			return batch
	
	# If no single batch has sufficient quantity, return the first batch
	return batches[0] if batches else None

@frappe.whitelist()
def release_quarantined_batch(batch_no, release_reason):
	"""
	Release a quarantined batch
	
	Parameters:
	- batch_no: Batch number
	- release_reason: Reason for release
	
	Returns:
	- Success message
	"""
	batch_name = _resolve_pharma_batch_name(batch_no)
	batch = frappe.get_doc("Pharma Batch", batch_name)
	
	if batch.quality_status != "Quarantined":
		frappe.throw(_("Batch {0} is not quarantined").format(batch_no))
	
	frappe.db.set_value(
		"Pharma Batch",
		batch_name,
		{
			"quality_status": "Approved",
			"quarantine_reason": None,
			"quarantine_date": None,
			"release_date": getdate(),
		},
		update_modified=True,
	)
	
	return {"success": True, "message": _("Batch {0} released from quarantine").format(batch_no)}

@frappe.whitelist()
def quarantine_batch(batch_no, quarantine_reason):
	"""
	Quarantine a batch
	
	Parameters:
	- batch_no: Batch number
	- quarantine_reason: Reason for quarantine
	
	Returns:
	- Success message
	"""
	batch_name = _resolve_pharma_batch_name(batch_no)
	batch = frappe.get_doc("Pharma Batch", batch_name)
	
	if batch.quality_status == "Quarantined":
		frappe.throw(_("Batch {0} is already quarantined").format(batch_no))
	
	frappe.db.set_value(
		"Pharma Batch",
		batch_name,
		{
			"quality_status": "Quarantined",
			"quarantine_reason": quarantine_reason,
			"quarantine_date": getdate(),
			"release_date": None,
		},
		update_modified=True,
	)
	
	return {"success": True, "message": _("Batch {0} placed in quarantine").format(batch_no)}


def _resolve_pharma_batch_name(batch_ref, throw=True):
	if frappe.db.exists("Pharma Batch", batch_ref):
		return batch_ref

	batch_name = frappe.db.get_value("Pharma Batch", {"batch_number": batch_ref}, "name")
	if batch_name:
		return batch_name

	if throw:
		frappe.throw(_("Pharma Batch {0} not found").format(batch_ref))
	return None

@frappe.whitelist()
def get_batch_stock_summary(batch_no):
	"""
	Get stock summary for a batch
	
	Parameters:
	- batch_no: Batch number
	
	Returns:
	- Stock summary with warehouse-wise quantities
	"""
	from frappe.query_builder import DocType, functions as fn
	
	bin = DocType("Bin")
	
	query = (
		frappe.qb.from_(bin)
		.select(
			bin.warehouse,
			fn.Sum(bin.actual_qty).as_("actual_qty"),
			fn.Sum(bin.projected_qty).as_("projected_qty"),
			fn.Sum(bin.reserved_qty).as_("reserved_qty")
		)
		.where(bin.batch_no == batch_no)
		.groupby(bin.warehouse)
	)
	
	stock_data = query.run(as_dict=True)
	
	# Calculate totals
	total_actual = sum([s.actual_qty or 0 for s in stock_data])
	total_projected = sum([s.projected_qty or 0 for s in stock_data])
	total_reserved = sum([s.reserved_qty or 0 for s in stock_data])
	
	return {
		"warehouse_stock": stock_data,
		"total_actual_qty": total_actual,
		"total_projected_qty": total_projected,
		"total_reserved_qty": total_reserved
	}

@frappe.whitelist()
def get_batch_movement_history(batch_no, limit=50):
	"""
	Get movement history for a batch
	
	Parameters:
	- batch_no: Batch number
	- limit: Number of records to return
	
	Returns:
	- Movement history records
	"""
	from frappe.query_builder import DocType
	
	stock_ledger = DocType("Stock Ledger Entry")
	
	query = (
		frappe.qb.from_(stock_ledger)
		.select(
			stock_ledger.name,
			stock_ledger.posting_date,
			stock_ledger.posting_time,
			stock_ledger.voucher_type,
			stock_ledger.voucher_no,
			stock_ledger.warehouse,
			stock_ledger.actual_qty,
			stock_ledger.qty_after_transaction
		)
		.where(stock_ledger.batch_no == batch_no)
		.orderby(stock_ledger.posting_date, stock_ledger.posting_time, order="DESC")
		.limit(limit)
	)
	
	movement_history = query.run(as_dict=True)
	
	return movement_history
