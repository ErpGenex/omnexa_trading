# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class FieldPermission(Document):
	def validate(self):
		self._validate_permission_name()
		self._validate_doctype_field()

	def _validate_permission_name(self):
		"""Validate permission name is unique"""
		if not self.permission_name:
			target_dt = self.get("target_doctype") or "Unknown"
			self.permission_name = f"FP-{target_dt}-{self.field_name}-{self.role}"
		
		if frappe.db.exists("Field Permission", {
			"permission_name": self.permission_name,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Permission Name {0} already exists").format(self.permission_name))

	def _validate_doctype_field(self):
		"""Validate that the field exists in the DocType"""
		target_dt = self.get("target_doctype")
		if not target_dt:
			return
		meta = frappe.get_meta(target_dt)
		field_exists = False
		
		for field in meta.fields:
			if field.fieldname == self.field_name:
				field_exists = True
				break
		
		if not field_exists:
			frappe.throw(_("Field {0} does not exist in DocType {1}").format(self.field_name, target_dt))

@frappe.whitelist()
def check_field_permission(doctype, field_name, user=None):
	"""
	Check if a user has permission to access a field
	
	Parameters:
	- doctype: DocType name
	- field_name: Field name
	- user: User (optional, defaults to current user)
	
	Returns:
	- Dictionary with read, write, mask, hide permissions
	"""
	if not user:
		user = frappe.session.user
	
	# Get user roles
	roles = frappe.get_roles(user)
	
	# Check field permissions for each role
	permissions = {
		"read": True,
		"write": True,
		"mask": False,
		"hide": False
	}
	
	for role in roles:
		field_perms = frappe.get_all("Field Permission", {
			"target_doctype": doctype,
			"field_name": field_name,
			"role": role,
			"status": "Active"
		}, ["read_permission", "write_permission", "mask_permission", "hide_permission", "condition"])
		
		for perm in field_perms:
			# Apply permissions (most restrictive)
			if not perm.read_permission:
				permissions["read"] = False
			if not perm.write_permission:
				permissions["write"] = False
			if perm.mask_permission:
				permissions["mask"] = True
			if perm.hide_permission:
				permissions["hide"] = True
	
	return permissions

@frappe.whitelist()
def mask_field_value(doctype, field_name, value, user=None):
	"""
	Mask field value based on field permissions
	
	Parameters:
	- doctype: DocType name
	- field_name: Field name
	- value: Field value
	- user: User (optional, defaults to current user)
	
	Returns:
	- Masked value or original value
	"""
	permissions = check_field_permission(doctype, field_name, user)
	
	if permissions.get("hide"):
		return None
	elif permissions.get("mask"):
		# Mask the value (show only last 4 characters)
		if value and len(str(value)) > 4:
			return "*" * (len(str(value)) - 4) + str(value)[-4:]
		return value
	else:
		return value

@frappe.whitelist()
def get_field_permissions_for_doctype(doctype):
	"""Get all field permissions for a DocType"""
	permissions = frappe.get_all("Field Permission", {
		"target_doctype": doctype,
		"status": "Active"
	}, ["name", "permission_name", "field_name", "role", "read_permission", "write_permission", "mask_permission", "hide_permission"])
	
	return permissions
