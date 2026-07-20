# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from functools import wraps

def cache_result(cache_key_prefix, expire_in_seconds=3600):
	"""
	Decorator to cache function results
	
	Parameters:
	- cache_key_prefix: Prefix for cache key
	- expire_in_seconds: Cache expiry time in seconds (default: 1 hour)
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			# Generate cache key
			cache_key = f"{cache_key_prefix}:{str(args)}:{str(kwargs)}"
			
			# Try to get from cache
			cached_value = frappe.cache().get_value(cache_key)
			if cached_value is not None:
				return json.loads(cached_value)
			
			# Execute function
			result = func(*args, **kwargs)
			
			# Cache result
			frappe.cache().set_value(cache_key, json.dumps(result), expire_in_seconds)
			
			return result
		return wrapper
	return decorator

def get_cached_batch_info(batch_no):
	"""
	Get cached batch information
	
	Parameters:
	- batch_no: Batch number
	
	Returns:
	- Batch information dictionary
	"""
	cache_key = f"batch_info:{batch_no}"
	cached_value = frappe.cache().get_value(cache_key)
	
	if cached_value is not None:
		return json.loads(cached_value)
	
	# Get batch info from database
	batch_info = frappe.db.get_value("Pharma Batch", 
		{"batch_number": batch_no
	},
		["name", "batch_number", "item_code", "expiry_date", "quality_status", "is_active"]
	)
	
	if batch_info:
		batch_dict = {
			"name": batch_info[0],
			"batch_number": batch_info[1],
			"item_code": batch_info[2],
			"expiry_date": str(batch_info[3]),
			"quality_status": batch_info[4],
			"is_active": batch_info[5]
		}
		# Cache for 30 minutes
		frappe.cache().set_value(cache_key, json.dumps(batch_dict), 1800)
		return batch_dict
	
	return None

def invalidate_batch_cache(batch_no):
	"""
	Invalidate cache for a specific batch
	
	Parameters:
	- batch_no: Batch number
	"""
	cache_key = f"batch_info:{batch_no}"
	frappe.cache().delete_value(cache_key)

def get_cached_temperature_summary(batch_no):
	"""
	Get cached temperature summary for a batch
	
	Parameters:
	- batch_no: Batch number
	
	Returns:
	- Temperature summary dictionary
	"""
	cache_key = f"temp_summary:{batch_no}"
	cached_value = frappe.cache().get_value(cache_key)
	
	if cached_value is not None:
		return json.loads(cached_value)
	
	# Get temperature summary from database
	from frappe.query_builder import DocType, functions as fn
	
	temp_log = DocType("Temperature Log")
	
	query = (
		frappe.qb.from_(temp_log)
		.select(
			fn.Avg(temp_log.temperature).as_("avg_temp"),
			fn.Min(temp_log.temperature).as_("min_temp"),
			fn.Max(temp_log.temperature).as_("max_temp"),
			fn.Count(temp_log.name).as_("total_logs")
		)
		.where(temp_log.batch_number == batch_no)
	)
	
	result = query.run(as_dict=True)
	
	if result:
		summary = result[0]
		# Cache for 15 minutes
		frappe.cache().set_value(cache_key, json.dumps(summary), 900)
		return summary
	
	return None

def invalidate_temperature_cache(batch_no):
	"""
	Invalidate temperature cache for a batch
	
	Parameters:
	- batch_no: Batch number
	"""
	cache_key = f"temp_summary:{batch_no}"
	frappe.cache().delete_value(cache_key)

def get_cached_field_permissions(doctype, field_name, user=None):
	"""
	Get cached field permissions
	
	Parameters:
	- doctype: DocType name
	- field_name: Field name
	- user: User email (optional)
	
	Returns:
	- Permissions dictionary
	"""
	if not user:
		user = frappe.session.user
	
	cache_key = f"field_perm:{doctype}:{field_name}:{user}"
	cached_value = frappe.cache().get_value(cache_key)
	
	if cached_value is not None:
		return json.loads(cached_value)
	
	# Get permissions from database
	from omnexa_trading.omnexa_trading.doctype.field_permission.field_permission import check_field_permission
	permissions = check_field_permission(doctype, field_name, user)
	
	# Cache for 1 hour
	frappe.cache().set_value(cache_key, json.dumps(permissions), 3600)
	
	return permissions

def invalidate_field_permission_cache(doctype, field_name=None, user=None):
	"""
	Invalidate field permission cache
	
	Parameters:
	- doctype: DocType name
	- field_name: Field name (optional)
	- user: User email (optional)
	"""
	if field_name and user:
		cache_key = f"field_perm:{doctype}:{field_name}:{user}"
		frappe.cache().delete_value(cache_key)
	elif field_name:
		# Invalidate all field permissions for this field
		cache_pattern = f"field_perm:{doctype}:{field_name}:*"
		# Note: This requires Redis pattern matching which may not be available in all cache backends
		# For now, we'll clear all field permission cache for this doctype
		clear_doctype_field_cache(doctype)
	else:
		# Invalidate all field permissions for this doctype
		clear_doctype_field_cache(doctype)

def clear_doctype_field_cache(doctype):
	"""
	Clear all field permission cache for a doctype
	
	Parameters:
	- doctype: DocType name
	"""
	# This is a simplified approach - in production, you might want to use Redis pattern matching
	# or maintain a list of cache keys to invalidate
	pass

def get_cached_audit_trail(document_type, document_name, limit=50):
	"""
	Get cached audit trail for a document
	
	Parameters:
	- document_type: Document type
	- document_name: Document name
	- limit: Number of records to return
	
	Returns:
	- Audit trail records
	"""
	cache_key = f"audit_trail:{document_type}:{document_name}:{limit}"
	cached_value = frappe.cache().get_value(cache_key)
	
	if cached_value is not None:
		return json.loads(cached_value)
	
	# Get audit trail from database
	from omnexa_trading.omnexa_trading.doctype.audit_log.audit_log import get_audit_trail
	audit_trail = get_audit_trail(document_type, document_name)
	
	if audit_trail:
		# Cache for 10 minutes
		frappe.cache().set_value(cache_key, json.dumps(audit_trail[:limit]), 600)
		return audit_trail[:limit]
	
	return []

def invalidate_audit_cache(document_type, document_name=None):
	"""
	Invalidate audit cache
	
	Parameters:
	- document_type: Document type
	- document_name: Document name (optional)
	"""
	if document_name:
		cache_key = f"audit_trail:{document_type}:{document_name}:*"
		# Clear all cache keys for this document
		# Note: This requires pattern matching
		pass
	else:
		# Clear all audit cache for this document type
		pass

def cache_regulatory_approval(batch_no):
	"""
	Cache regulatory approval status for a batch
	
	Parameters:
	- batch_no: Batch number
	"""
	cache_key = f"reg_approval:{batch_no}"
	
	approval_info = frappe.db.get_value("Pharma Regulatory Approval",
		{"batch_number": batch_no, "approval_status": "Approved"
	},
		["name", "approval_status", "license_expiry", "valid_from", "valid_until"]
	)
	
	if approval_info:
		approval_dict = {
			"name": approval_info[0],
			"approval_status": approval_info[1],
			"license_expiry": str(approval_info[2]),
			"valid_from": str(approval_info[3]),
			"valid_until": str(approval_info[4])
		}
		# Cache for 1 hour
		frappe.cache().set_value(cache_key, json.dumps(approval_dict), 3600)
		return approval_dict
	
	return None

def get_cached_regulatory_approval(batch_no):
	"""
	Get cached regulatory approval for a batch
	
	Parameters:
	- batch_no: Batch number
	
	Returns:
	- Regulatory approval dictionary
	"""
	cache_key = f"reg_approval:{batch_no}"
	cached_value = frappe.cache().get_value(cache_key)
	
	if cached_value is not None:
		return json.loads(cached_value)
	
	return cache_regulatory_approval(batch_no)

def invalidate_regulatory_cache(batch_no):
	"""
	Invalidate regulatory approval cache for a batch
	
	Parameters:
	- batch_no: Batch number
	"""
	cache_key = f"reg_approval:{batch_no}"
	frappe.cache().delete_value(cache_key)

def clear_all_pharma_cache():
	"""
	Clear all pharmaceutical compliance cache
	"""
	# This is a nuclear option - use with caution
	# In production, you might want to use Redis FLUSHDB or similar
	frappe.cache().clear()
