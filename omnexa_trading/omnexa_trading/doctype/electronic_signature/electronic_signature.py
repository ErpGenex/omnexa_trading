# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, get_datetime, getdate
from frappe.model.document import Document
import hashlib
import json
import secrets

class ElectronicSignature(Document):
	def validate(self):
		self._validate_signature_uniqueness()
		self._validate_user()
		self._validate_document()
		self._generate_signature_id()
		self._generate_document_hash()
		self._generate_signature_binding()
		self._set_user_full_name()
	
	def before_save(self):
		self._capture_authentication_details()
	
	def on_submit(self):
		self._verify_signature()
		self._log_signature_event()
		self._update_document_signature_status()
	
	def on_cancel(self):
		self._revoke_signature()
		self._update_document_signature_status()
	
	def _validate_signature_uniqueness(self):
		"""Validate that signature is unique for this document"""
		if self.status == "Active":
			existing = frappe.db.exists("Electronic Signature", {
				"document_type": self.document_type,
				"document_name": self.document_name,
				"status": "Active",
				"name": ["!=", self.name]
			})
			if existing:
				frappe.throw(_("An active signature already exists for this document"))
	
	def _validate_user(self):
		"""Validate user and permissions"""
		if not self.user:
			frappe.throw(_("User is required"))
		
		# Check if user has permission to sign this document type
		has_permission = frappe.has_permission(self.document_type, "write", user=self.user)
		if not has_permission:
			frappe.throw(_("User does not have permission to sign this document type"))
	
	def _validate_document(self):
		"""Validate document exists and is in valid state"""
		if not self.document_type or not self.document_name:
			frappe.throw(_("Document type and name are required"))
		
		# Check if document exists
		if not frappe.db.exists(self.document_type, self.document_name):
			frappe.throw(_("Document {0} {1} does not exist").format(self.document_type, self.document_name))
		
		# Check document status
		doc = frappe.get_doc(self.document_type, self.document_name)
		if hasattr(doc, 'docstatus') and doc.docstatus != 1:
			frappe.throw(_("Document must be submitted before signing"))
	
	def _generate_signature_id(self):
		"""Generate unique signature ID"""
		if not self.signature_id:
			self.signature_id = f"SIG-{secrets.token_hex(16).upper()}"
	
	def _generate_document_hash(self):
		"""Generate hash of document content for integrity verification"""
		if not self.document_hash:
			doc = frappe.get_doc(self.document_type, self.document_name)
			doc_content = json.dumps(doc.as_dict(), sort_keys=True)
			self.document_hash = hashlib.sha256(doc_content.encode()).hexdigest()
	
	def _generate_signature_binding(self):
		"""Generate cryptographic binding between signature and document"""
		if not self.signature_binding:
			binding_data = {
				"signature_id": self.signature_id,
				"document_hash": self.document_hash,
				"user": self.user,
				"timestamp": str(now())
			}
			self.signature_binding = hashlib.sha256(json.dumps(binding_data).encode()).hexdigest()
	
	def _set_user_full_name(self):
		"""Set user full name from user record"""
		if self.user and not self.user_full_name:
			user = frappe.get_doc("User", self.user)
			self.user_full_name = user.full_name or user.email
	
	def _capture_authentication_details(self):
		"""Capture authentication details for compliance"""
		if not self.authentication_timestamp:
			self.authentication_timestamp = now()
		
		# Capture IP address (in production, this would come from request headers)
		if not self.ip_address:
			self.ip_address = frappe.request.environ.get("REMOTE_ADDR", "127.0.0.1")
		
		# Generate authentication token
		if not self.authentication_token:
			self.authentication_token = secrets.token_urlsafe(32)
	
	def _verify_signature(self):
		"""Verify signature authenticity and integrity"""
		self.verification_status = "Verified"
		self.verification_timestamp = now()
		self.verification_method = "Cryptographic Hash Verification"
		
		# Verify document hash hasn't changed
		doc = frappe.get_doc(self.document_type, self.document_name)
		doc_content = json.dumps(doc.as_dict(), sort_keys=True)
		current_hash = hashlib.sha256(doc_content.encode()).hexdigest()
		
		if current_hash != self.document_hash:
			self.verification_status = "Failed"
			self.verification_notes = _("Document hash mismatch - document may have been modified")
		
		# Verify signature binding
		binding_data = {
			"signature_id": self.signature_id,
			"document_hash": self.document_hash,
			"user": self.user,
			"timestamp": str(self.authentication_timestamp)
		}
		expected_binding = hashlib.sha256(json.dumps(binding_data).encode()).hexdigest()
		
		if expected_binding != self.signature_binding:
			self.verification_status = "Failed"
			self.verification_notes = _("Signature binding verification failed")
		
		self.verification_hash = hashlib.sha256(
			(self.signature_binding + current_hash).encode()
		).hexdigest()
	
	def _log_signature_event(self):
		"""Log signature event to audit trail"""
		frappe.get_doc({
			"doctype": "Event Audit Log",
			"event_type": "Sign",
			"document_type": self.document_type,
			"document_name": self.document_name,
			"event_details": f"Electronic signature applied by {self.user_full_name} ({self.signature_type
	})"
		}).insert()
	
	def _update_document_signature_status(self):
		"""Update document with signature status"""
		try:
			doc = frappe.get_doc(self.document_type, self.document_name)
			if hasattr(doc, 'electronic_signature'):
				doc.electronic_signature = self.name
				doc.electronic_signature_status = self.status
				doc.electronic_signature_date = self.signature_date
				doc.save(ignore_permissions=True)
		except:
			# Document may not have signature fields
			pass
	
	def _revoke_signature(self):
		"""Revoke electronic signature"""
		self.status = "Revoked"
		self.revocation_date = getdate()
		self.revocation_by = frappe.session.user
		
		# Log revocation to audit trail
		frappe.get_doc({
			"doctype": "Event Audit Log",
			"event_type": "Revoke Signature",
			"document_type": self.document_type,
			"document_name": self.document_name,
			"event_details": f"Electronic signature revoked by {self.revocation_by}. Reason: {self.revocation_reason
	}"
		}).insert()

@frappe.whitelist()
def create_electronic_signature(document_type, document_name, signature_type, signature_purpose, authentication_method="Password"):
	"""
	Create an electronic signature for a document
	
	Parameters:
	- document_type: Type of document to sign
	- document_name: Name of document to sign
	- signature_type: Type of signature (Approval, Authorization, etc.)
	- signature_purpose: Purpose of the signature
	- authentication_method: Method of authentication (Password, MFA, etc.)
	
	Returns:
	- Signature name if successful
	"""
	# Validate user authentication (in production, this would verify actual credentials)
	if not frappe.session.user:
		frappe.throw(_("User must be logged in to create signature"))
	
	# Create signature
	signature = frappe.get_doc({
		"doctype": "Electronic Signature",
		"signature_name": f"{signature_type} - {document_name
	}",
		"signature_type": signature_type,
		"signature_purpose": signature_purpose,
		"user": frappe.session.user,
		"signature_date": getdate(),
		"signature_time": frappe.utils.nowtime(),
		"document_type": document_type,
		"document_name": document_name,
		"authentication_method": authentication_method,
		"status": "Active"
	})
	
	signature.insert()
	signature.submit()
	
	return signature.name

@frappe.whitelist()
def verify_electronic_signature(signature_id):
	"""
	Verify an electronic signature
	
	Parameters:
	- signature_id: ID of signature to verify
	
	Returns:
	- Verification status and details
	"""
	signature = frappe.get_doc("Electronic Signature", signature_id)
	
	return {
		"signature_id": signature.signature_id,
		"verification_status": signature.verification_status,
		"verification_timestamp": signature.verification_timestamp,
		"verification_method": signature.verification_method,
		"verification_hash": signature.verification_hash,
		"verification_notes": signature.verification_notes,
		"status": signature.status,
		"user": signature.user,
		"user_full_name": signature.user_full_name,
		"signature_date": signature.signature_date,
		"signature_time": signature.signature_time
	}

@frappe.whitelist()
def revoke_electronic_signature(signature_id, revocation_reason):
	"""
	Revoke an electronic signature
	
	Parameters:
	- signature_id: ID of signature to revoke
	- revocation_reason: Reason for revocation
	
	Returns:
	- Success status
	"""
	signature = frappe.get_doc("Electronic Signature", signature_id)
	
	if signature.status != "Active":
		frappe.throw(_("Only active signatures can be revoked"))
	
	signature.revocation_reason = revocation_reason
	signature.cancel()
	
	return {"success": True, "message": "Signature revoked successfully"
	}

@frappe.whitelist()
def get_document_signatures(document_type, document_name):
	"""
	Get all signatures for a document
	
	Parameters:
	- document_type: Type of document
	- document_name: Name of document
	
	Returns:
	- List of signatures
	"""
	signatures = frappe.get_all("Electronic Signature",
		filters={
			"document_type": document_type,
			"document_name": document_name
		},
		fields=["name", "signature_id", "signature_type", "user", "user_full_name", 
		       "signature_date", "signature_time", "status", "verification_status"],
		order_by="signature_date DESC, signature_time DESC"
	)
	
	return signatures

@frappe.whitelist()
def check_signature_required(document_type, document_name):
	"""
	Check if a signature is required for a document
	
	Parameters:
	- document_type: Type of document
	- document_name: Name of document
	
	Returns:
	- Whether signature is required and what type
	"""
	# Check if document has active signature
	existing_signature = frappe.db.exists("Electronic Signature", {
		"document_type": document_type,
		"document_name": document_name,
		"status": "Active"
	})
	
	if existing_signature:
		return {"required": False, "message": "Document already has active signature"
	}
	
	# Check document type signature requirements (configurable)
	signature_requirements = {
		"Pharma Quality Inspection": {"required": True, "type": "Approval"
	},
		"Pharma Regulatory Approval": {"required": True, "type": "Authorization"
	},
		"Pharma Product Recall": {"required": True, "type": "Authorization"
	},
		"Temperature Excursion": {"required": True, "type": "Verification"
	},
		"CAPA": {"required": True, "type": "Approval"
	},
		"Deviation": {"required": True, "type": "Verification"
	}
	}
	
	requirement = signature_requirements.get(document_type, {"required": False, "type": None
	})
	
	return requirement
