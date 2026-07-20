import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

class PharmaDrugRegistration(Document):
	def validate(self):
		self.validate_drug_code()
		self.validate_pricing()
		self.validate_controlled_substance()
		self.validate_expiry_tracking()
	
	def on_submit(self):
		self.create_or_update_item()
		self.update_pricing_history()
	
	def on_update_after_submit(self):
		self.check_price_changes()
	
	def validate_drug_code(self):
		"""Ensure drug code is unique"""
		if self.drug_code:
			existing = frappe.db.exists("Pharma Drug Registration", {
				"drug_code": self.drug_code,
				"name": ("!=", self.name)
			})
			if existing:
				frappe.throw(f"Drug Code {self.drug_code} already exists")
	
	def validate_pricing(self):
		"""Validate pricing structure"""
		if self.maximum_retail_price and self.wholesale_price:
			if self.wholesale_price > self.maximum_retail_price:
				frappe.throw("Wholesale price cannot exceed Maximum Retail Price")
		
		if self.pharmacy_price and self.maximum_retail_price:
			if self.pharmacy_price > self.maximum_retail_price:
				frappe.throw("Pharmacy price cannot exceed Maximum Retail Price")
		
		if self.distributor_price and self.wholesale_price:
			if self.distributor_price > self.wholesale_price:
				frappe.throw("Distributor price cannot exceed Wholesale Price")
	
	def validate_controlled_substance(self):
		"""Validate controlled substance requirements"""
		if self.is_controlled:
			if not self.schedule_class:
				frappe.throw("Schedule Class is required for Controlled Substances")
			if not self.government_registration_number:
				frappe.throw("Government Registration Number is required for Controlled Substances")
	
	def validate_expiry_tracking(self):
		"""Ensure expiry tracking for pharmaceutical items"""
		if not self.expiry_tracking:
			frappe.msgprint("Warning: Expiry tracking is disabled for this drug")
		
		if self.cold_chain_required and self.storage_temperature != "Refrigerated (2-8°C)":
			frappe.msgprint("Warning: Cold chain required but storage temperature is not set to Refrigerated")
	
	def create_or_update_item(self):
		"""Create or update Item in ERP"""
		if not frappe.db.exists("Item", self.drug_code):
			item = frappe.new_doc("Item")
			item.item_code = self.drug_code
			item.item_name = self.drug_name
			item.item_group = self.drug_category or "All Item Groups"
			item.description = f"{self.drug_name} - {self.generic_name or ''} - {self.strength or ''}"
			item.stock_uom = "Nos"
			item.is_stock_item = 1
			item.has_batch_no = self.batch_tracking
			item.has_expiry_date = self.expiry_tracking
			item.has_serial_no = self.serial_tracking
			item.include_item_in_manufacturing = 0
			item.is_fixed_asset = 0
			item.disabled = not self.is_active
			item.item_defaults = [{
				"company": self.company or frappe.db.get_single_value("Global Defaults", "default_company"),
				"default_warehouse": "Main Warehouse - Cairo"
			}]
			item.insert()
			frappe.msgprint(f"Item {self.drug_code} created successfully")
		else:
			item = frappe.get_doc("Item", self.drug_code)
			item.item_name = self.drug_name
			item.item_group = self.drug_category or "All Item Groups"
			item.description = f"{self.drug_name} - {self.generic_name or ''} - {self.strength or ''}"
			item.has_batch_no = self.batch_tracking
			item.has_expiry_date = self.expiry_tracking
			item.has_serial_no = self.serial_tracking
			item.disabled = not self.is_active
			item.save()
			frappe.msgprint(f"Item {self.drug_code} updated successfully")
	
	def update_pricing_history(self):
		"""Record initial pricing in history"""
		price_types = [
			{"field": "maximum_retail_price", "type": "Maximum Retail Price"
	},
			{"field": "wholesale_price", "type": "Wholesale Price"
	},
			{"field": "pharmacy_price", "type": "Pharmacy Price"
	},
			{"field": "distributor_price", "type": "Distributor Price"
	},
			{"field": "hospital_price", "type": "Hospital Price"
	}
		]
		
		for price in price_types:
			price_value = self.get(price["field"])
			if price_value:
				self.append("pricing_history", {
					"price_type": price["type"],
					"old_price": 0,
					"new_price": price_value,
					"effective_date": today(),
					"currency": self.currency,
					"reason_for_change": "Initial Price",
					"changed_by": frappe.session.user,
					"change_date": frappe.utils.now()
				})
	
	def check_price_changes(self):
		"""Check if prices have changed and record in history"""
		if not self.pricing_history:
			return
		
		price_types = [
			{"field": "maximum_retail_price", "type": "Maximum Retail Price"
	},
			{"field": "wholesale_price", "type": "Wholesale Price"
	},
			{"field": "pharmacy_price", "type": "Pharmacy Price"
	},
			{"field": "distributor_price", "type": "Distributor Price"
	},
			{"field": "hospital_price", "type": "Hospital Price"
	}
		]
		
		for price in price_types:
			price_value = self.get(price["field"])
			if price_value:
				# Get last price for this type
				last_price = frappe.get_value("Pharma Drug Pricing History", {
					"parent": self.name,
					"price_type": price["type"]
				}, "new_price", order_by="creation desc")
				
				if last_price and flt(last_price) != flt(price_value):
					self.append("pricing_history", {
						"price_type": price["type"],
						"old_price": last_price,
						"new_price": price_value,
						"effective_date": today(),
						"currency": self.currency,
						"reason_for_change": "Price Update",
						"changed_by": frappe.session.user,
						"change_date": frappe.utils.now()
					})

