# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, now_datetime
import hashlib
import base64
from cryptography.fernet import Fernet

class EncryptionKey(Document):
	def validate(self):
		self._validate_key_name()
		self._generate_key_hash()
		self._set_created_date()
		self._calculate_next_rotation_date()

	def _validate_key_name(self):
		"""Validate key name is unique"""
		if not self.key_name:
			self.key_name = f"KEY-{self.algorithm}-{now_datetime().strftime('%Y%m%d')}"
		
		if frappe.db.exists("Encryption Key", {
			"key_name": self.key_name,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Key Name {0} already exists").format(self.key_name))

	def _generate_key_hash(self):
		"""Generate hash of the key value for verification"""
		if self.key_value:
			self.key_hash = hashlib.sha256(self.key_value.encode()).hexdigest()

	def _set_created_date(self):
		"""Set created date if not set"""
		if not self.created_date:
			self.created_date = nowdate()

	def _calculate_next_rotation_date(self):
		"""Calculate next rotation date based on frequency"""
		if self.rotation_frequency and self.last_rotation_date:
			from frappe.utils import add_months, add_years
			
			if self.rotation_frequency == "Monthly":
				self.next_rotation_date = add_months(self.last_rotation_date, 1)
			elif self.rotation_frequency == "Quarterly":
				self.next_rotation_date = add_months(self.last_rotation_date, 3)
			elif self.rotation_frequency == "Semi-Annually":
				self.next_rotation_date = add_months(self.last_rotation_date, 6)
			elif self.rotation_frequency == "Annually":
				self.next_rotation_date = add_years(self.last_rotation_date, 1)

@frappe.whitelist()
def generate_encryption_key(algorithm="AES", key_length=256):
	"""
	Generate a new encryption key
	
	Parameters:
	- algorithm: Encryption algorithm (AES, RSA, Fernet)
	- key_length: Key length in bits
	
	Returns:
	- Generated key
	"""
	if algorithm == "Fernet":
		key = Fernet.generate_key()
		return key.decode('utf-8')
	elif algorithm == "AES":
		# Generate random key
		import secrets
		key = secrets.token_bytes(key_length // 8)
		return base64.b64encode(key).decode('utf-8')
	else:
		import secrets
		key = secrets.token_bytes(key_length // 8)
		return base64.b64encode(key).decode('utf-8')

def _get_encryption_key(key_name):
	name = frappe.db.get_value("Encryption Key", {"key_name": key_name, "active": 1
	}, "name")
	if not name:
		frappe.throw(_("Active encryption key {0} not found").format(key_name))
	key = frappe.get_doc("Encryption Key", name)
	key_value = key.get_password("key_value")
	return key, key_value

@frappe.whitelist()
def encrypt_data(data, key_name):
	"""
	Encrypt data using specified encryption key
	
	Parameters:
	- data: Data to encrypt
	- key_name: Name of encryption key to use
	
	Returns:
	- Encrypted data
	"""
	key, key_value = _get_encryption_key(key_name)
	
	if key.algorithm == "Fernet":
		f = Fernet(key_value.encode())
		encrypted = f.encrypt(data.encode())
		return encrypted.decode('utf-8')
	elif key.algorithm == "AES":
		from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
		from cryptography.hazmat.backends import default_backend
		import os
		
		key_bytes = base64.b64decode(key_value)
		iv = os.urandom(16)
		cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
		encryptor = cipher.encryptor()
		
		# Pad data to block size
		padded_data = data.encode() + b' ' * (16 - len(data.encode()) % 16)
		encrypted = encryptor.update(padded_data) + encryptor.finalize()
		
		return base64.b64encode(iv + encrypted).decode('utf-8')
	else:
		frappe.throw(_("Algorithm {0} not supported").format(key.algorithm))

@frappe.whitelist()
def decrypt_data(encrypted_data, key_name):
	"""
	Decrypt data using specified encryption key
	
	Parameters:
	- encrypted_data: Data to decrypt
	- key_name: Name of encryption key to use
	
	Returns:
	- Decrypted data
	"""
	key, key_value = _get_encryption_key(key_name)
	
	if key.algorithm == "Fernet":
		f = Fernet(key_value.encode())
		decrypted = f.decrypt(encrypted_data.encode())
		return decrypted.decode('utf-8')
	elif key.algorithm == "AES":
		from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
		from cryptography.hazmat.backends import default_backend
		
		key_bytes = base64.b64decode(key_value)
		encrypted_bytes = base64.b64decode(encrypted_data)
		iv = encrypted_bytes[:16]
		encrypted = encrypted_bytes[16:]
		
		cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
		decryptor = cipher.decryptor()
		decrypted = decryptor.update(encrypted) + decryptor.finalize()
		
		return decrypted.decode('utf-8').strip()
	else:
		frappe.throw(_("Algorithm {0} not supported").format(key.algorithm))

@frappe.whitelist()
def rotate_key(key_name):
	"""
	Rotate encryption key
	
	Parameters:
	- key_name: Name of key to rotate
	
	Returns:
	- New key name
	"""
	old_key = frappe.get_doc("Encryption Key", {"key_name": key_name
	})
	
	# Generate new key
	new_key_value = generate_encryption_key(old_key.algorithm, old_key.key_length)
	
	# Create new key record
	new_key = frappe.new_doc("Encryption Key")
	new_key.key_name = f"{key_name}-ROTATED-{now_datetime().strftime('%Y%m%d')}"
	new_key.key_type = old_key.key_type
	new_key.algorithm = old_key.algorithm
	new_key.key_length = old_key.key_length
	new_key.key_value = new_key_value
	new_key.company = old_key.company
	new_key.rotation_frequency = old_key.rotation_frequency
	new_key.last_rotation_date = nowdate()
	new_key.active = 1
	new_key.status = "Active"
	new_key.save()
	
	# Deactivate old key
	old_key.active = 0
	old_key.status = "Inactive"
	old_key.save()
	
	return new_key.key_name
