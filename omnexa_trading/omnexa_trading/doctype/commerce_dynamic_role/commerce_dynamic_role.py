import frappe
from frappe import _
from frappe.model.document import Document

class CommerceDynamicRole(Document):
	def validate(self):
		"""Validate the dynamic role before saving"""
		self.validate_role_id_format()
		self.validate_unique_role_id()
		self.validate_portal_url_format()
		self.set_created_by()
	
	def on_update(self):
		"""Handle updates to the dynamic role"""
		self.update_frappe_role()
		self.update_workcenter()
	
	def on_trash(self):
		"""Handle deletion of the dynamic role"""
		self.remove_frappe_role()
		self.update_workcenter()
	
	def validate_role_id_format(self):
		"""Validate that role ID follows commerce_ format"""
		if self.role_id and not self.role_id.startswith("commerce_"):
			frappe.throw(_("Role ID must start with 'commerce_'"))
	
	def validate_unique_role_id(self):
		"""Validate that role ID is unique"""
		if self.role_id and frappe.db.exists("Commerce Dynamic Role", {
			"role_id": self.role_id,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Role ID already exists"))
	
	def validate_portal_url_format(self):
		"""Validate that portal URL follows correct format"""
		if self.portal_url and not self.portal_url.startswith("/app/commerce/"):
			frappe.throw(_("Portal URL must start with '/app/commerce/'"))
	
	def set_created_by(self):
		"""Set created by and creation date if new document"""
		if self.is_new():
			self.created_by = frappe.session.user
			self.creation_date = frappe.utils.now()
		else:
			self.modified_by = frappe.session.user
			self.modification_date = frappe.utils.now()
	
	def update_frappe_role(self):
		"""Update or create corresponding Frappe role"""
		if self.role_id:
			if frappe.db.exists("Role", self.role_id):
				# Update existing role
				role = frappe.get_doc("Role", self.role_id)
				role.role_name = self.role_name
				role.desk_access = 1
				role.save()
			else:
				# Create new role
				frappe.get_doc({
					"doctype": "Role",
					"role_name": self.role_id,
					"desk_access": 1
				}).insert()
	
	def remove_frappe_role(self):
		"""Remove corresponding Frappe role"""
		if self.role_id and frappe.db.exists("Role", self.role_id):
			# Check if role is being used by any user
			users_with_role = frappe.db.get_all("Has Role", {
				"role": self.role_id
			})
			
			if users_with_role:
				frappe.throw(_("Cannot remove role as it is assigned to users"))
			else:
				frappe.delete_doc("Role", self.role_id)
	
	def update_workcenter(self):
		"""Update workcenter to reflect changes"""
		# This will trigger a cache invalidation for the workcenter
		frappe.cache().delete_value("commerce_workcenter_portals")
	
	def get_permissions(self):
		"""Get permissions for this role"""
		permissions = {
			"allowed_doctypes": [],
			"restricted_doctypes": [],
			"allowed_actions": []
		}
		
		# Get allowed doctypes
		for doctype in self.allowed_doctypes:
			permissions["allowed_doctypes"].append(doctype.doctype_name)
		
		# Get restricted doctypes
		for doctype in self.restricted_doctypes:
			permissions["restricted_doctypes"].append(doctype.doctype_name)
		
		# Get allowed actions
		for action in self.allowed_actions:
			permissions["allowed_actions"].append(action.action_name)
		
		return permissions
	
	def get_dashboard_config(self):
		"""Get dashboard configuration"""
		if self.dashboard_config:
			try:
				return frappe.parse_json(self.dashboard_config)
			except:
				return {}
		return {}
	
	def get_sidebar_config(self):
		"""Get sidebar configuration"""
		if self.sidebar_config:
			try:
				return frappe.parse_json(self.sidebar_config)
			except:
				return {}
		return {}
