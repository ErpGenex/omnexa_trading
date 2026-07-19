import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, now

class PharmaImportLC(Document):
	def validate(self):
		self.validate_lc_amount()
		self.validate_dates()
		self.validate_bank_details()
		self.validate_items()
		self.calculate_total_landing_cost()
	
	def on_submit(self):
		self.update_status("Open")
		self.allocate_landing_cost_to_items()
		self.create_purchase_order()
	
	def on_cancel(self):
		self.update_status("Cancelled")
	
	def before_save(self):
		self.calculate_total_landing_cost()
	
	def validate_lc_amount(self):
		"""Validate LC amount against items total"""
		if self.lc_items:
			items_total = sum(flt(item.amount) for item in self.lc_items)
			if flt(self.lc_amount) < items_total:
				frappe.throw(f"LC Amount ({self.lc_amount}) is less than Items Total ({items_total})")
	
	def validate_dates(self):
		"""Validate LC and expiry dates"""
		if self.lc_date and self.expiry_date:
			if getdate(self.expiry_date) < getdate(self.lc_date):
				frappe.throw("Expiry Date cannot be before LC Date")
		
		if self.shipment_date and self.expiry_date:
			if getdate(self.shipment_date) > getdate(self.expiry_date):
				frappe.throw("Shipment Date cannot be after Expiry Date")
	
	def validate_bank_details(self):
		"""Ensure issuing bank is specified"""
		if not self.issuing_bank:
			frappe.throw("Issuing Bank is required")
	
	def validate_items(self):
		"""Validate LC items"""
		if not self.lc_items:
			frappe.throw("At least one item is required")
		
		for item in self.lc_items:
			if not item.drug_code:
				frappe.throw("Drug Code is required for all items")
			if not item.quantity or item.quantity <= 0:
				frappe.throw("Quantity must be greater than 0")
			if not item.rate or item.rate <= 0:
				frappe.throw("Rate must be greater than 0")
			item.amount = flt(item.quantity) * flt(item.rate)
	
	def calculate_total_landing_cost(self):
		"""Calculate total landing cost from all charges"""
		lc_charges = (
			flt(self.lc_opening_charges) +
			flt(self.lc_amendment_charges) +
			flt(self.lc_confirmation_charges)
		)
		
		shipping_charges = (
			flt(self.freight_charges) +
			flt(self.insurance_charges) +
			flt(self.customs_duties) +
			flt(self.port_charges) +
			flt(self.container_charges) +
			flt(self.demurrage_charges) +
			flt(self.transportation_charges)
		)
		
		self.total_landing_cost = lc_charges + shipping_charges
	
	def allocate_landing_cost_to_items(self):
		"""Allocate landing cost to items based on allocation method"""
		if not self.lc_items or not self.allocate_to_items:
			return
		
		total_items_value = sum(flt(item.amount) for item in self.lc_items)
		if total_items_value == 0:
			return
		
		allocation_method = self.cost_allocation_method or "By Value"
		
		for item in self.lc_items:
			if allocation_method == "By Value":
				allocation_ratio = flt(item.amount) / total_items_value
			elif allocation_method == "By Quantity":
				total_quantity = sum(flt(i.quantity) for i in self.lc_items)
				allocation_ratio = flt(item.quantity) / total_quantity if total_quantity > 0 else 0
			else:
				allocation_ratio = flt(item.amount) / total_items_value
			
			item.landing_cost_allocated = flt(self.total_landing_cost) * allocation_ratio
			item.total_landed_cost = flt(item.amount) + item.landing_cost_allocated
			item.final_rate = item.total_landed_cost / flt(item.quantity) if item.quantity > 0 else 0
	
	def update_status(self, status):
		"""Update LC status"""
		self.status = status
		self.db_set("status", status)
	
	def create_purchase_order(self):
		"""Create Purchase Order from LC"""
		if not self.supplier:
			return
		
		try:
			po = frappe.new_doc("Purchase Order")
			po.supplier = self.supplier
			po.transaction_date = self.lc_date
			po.schedule_date = self.shipment_date or self.lc_date
			po.company = self.company or frappe.db.get_single_value("Global Defaults", "default_company")
			po.currency = self.currency
			
			for item in self.lc_items:
				po.append("items", {
					"item_code": item.drug_code,
					"item_name": item.drug_name,
					"qty": item.quantity,
					"uom": item.uom or "Nos",
					"rate": item.rate,
					"amount": item.amount
				})
			
			po.insert()
			po.submit()
			frappe.msgprint(f"Purchase Order {po.name} created from LC")
		except Exception as e:
			frappe.msgprint(f"Error creating Purchase Order: {str(e)}")
	
	def close_lc(self):
		"""Close the LC and record actual costs"""
		if self.status != "Open":
			frappe.throw("Only Open LCs can be closed")
		
		self.update_status("Closed")
		self.closing_date = today()
		self.closed_by = frappe.session.user
		
		if self.actual_landing_cost:
			self.variance_amount = flt(self.actual_landing_cost) - flt(self.total_landing_cost)
		
		self.save()
		frappe.msgprint(f"LC {self.name} closed successfully")

