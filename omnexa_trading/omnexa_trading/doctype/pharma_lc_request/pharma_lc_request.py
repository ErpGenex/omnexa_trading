import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, now

class PharmaLCRequest(Document):
	def validate(self):
		self.validate_request_amount()
		self.validate_supplier()
		self.validate_items()
		self.validate_dates()
	
	def on_submit(self):
		self.update_status("Pending Approval")
	
	def before_save(self):
		self.calculate_total_amount()
	
	def validate_request_amount(self):
		"""Validate LC amount against items total"""
		if self.request_items:
			items_total = sum(flt(item.estimated_amount) for item in self.request_items)
			if flt(self.lc_amount) < items_total:
				frappe.throw(f"LC Amount ({self.lc_amount}) is less than Estimated Items Total ({items_total})")
	
	def validate_supplier(self):
		"""Ensure supplier is specified"""
		if not self.supplier:
			frappe.throw("Supplier is required")
	
	def validate_items(self):
		"""Validate request items"""
		if not self.request_items:
			frappe.throw("At least one item is required")
		
		for item in self.request_items:
			if not item.drug_code:
				frappe.throw("Drug Code is required for all items")
			if not item.quantity or item.quantity <= 0:
				frappe.throw("Quantity must be greater than 0")
			if not item.estimated_rate or item.estimated_rate <= 0:
				frappe.throw("Estimated Rate must be greater than 0")
			item.estimated_amount = flt(item.quantity) * flt(item.estimated_rate)
	
	def validate_dates(self):
		"""Validate request and required by dates"""
		if self.required_by:
			if getdate(self.required_by) < getdate(self.request_date):
				frappe.throw("Required By Date cannot be before Request Date")
	
	def calculate_total_amount(self):
		"""Calculate total estimated amount from items"""
		if self.request_items:
			self.lc_amount = sum(flt(item.estimated_amount) for item in self.request_items)
	
	def update_status(self, status):
		"""Update request status"""
		self.status = status
		self.db_set("status", status)
	
	def approve_request(self):
		"""Approve the LC request"""
		if self.status != "Pending Approval":
			frappe.throw("Only Pending Approval requests can be approved")
		
		self.update_status("Approved")
		self.approved_by = frappe.session.user
		self.approval_date = now()
		self.save()
		frappe.msgprint(f"LC Request {self.name} approved successfully")
	
	def reject_request(self, reason):
		"""Reject the LC request"""
		if self.status != "Pending Approval":
			frappe.throw("Only Pending Approval requests can be rejected")
		
		self.update_status("Rejected")
		self.rejection_reason = reason
		self.save()
		frappe.msgprint(f"LC Request {self.name} rejected")
	
	def create_import_lc(self):
		"""Create Import LC from approved request"""
		if self.status != "Approved":
			frappe.throw("Only Approved requests can create Import LC")
		
		if self.import_lc:
			frappe.throw("Import LC already created for this request")
		
		try:
			lc = frappe.new_doc("Pharma Import LC")
			lc.lc_number = f"LC-{self.name.split('-')[-1]}"
			lc.lc_type = self.lc_type
			lc.lc_amount = self.lc_amount
			lc.currency = self.currency
			lc.lc_date = today()
			lc.expiry_date = self.required_by
			lc.issuing_bank = self.issuing_bank
			lc.advising_bank = self.advising_bank
			lc.lc_terms = self.lc_terms
			lc.payment_terms = self.payment_terms
			lc.supplier = self.supplier
			lc.company = self.company or frappe.db.get_single_value("Global Defaults", "default_company")
			
			# Copy items from request
			for item in self.request_items:
				lc.append("lc_items", {
					"drug_code": item.drug_code,
					"drug_name": item.drug_name,
					"description": item.description,
					"quantity": item.quantity,
					"uom": item.uom,
					"rate": item.estimated_rate,
					"amount": item.estimated_amount
				})
			
			lc.insert()
			self.import_lc = lc.name
			self.update_status("LC Opened")
			self.save()
			frappe.msgprint(f"Import LC {lc.name} created from request")
			return lc
		except Exception as e:
			frappe.throw(f"Error creating Import LC: {str(e)}")

