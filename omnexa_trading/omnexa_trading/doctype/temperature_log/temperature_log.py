# -*- coding: utf-8 -*-
# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, nowdate, nowtime

class TemperatureLog(Document):
	def validate(self):
		self._validate_log_number()
		self._validate_temperature()
		self._determine_temperature_status()
		self._check_excursion()
		self._populate_batch_details()

	def on_submit(self):
		self._create_excursion_if_needed()
		self._send_alert_if_needed()
		self.db_set("status", "Submitted")

	def _validate_log_number(self):
		"""Validate log number is unique"""
		if not self.log_number:
			self.log_number = f"TEMP-{now_datetime().strftime('%Y%m%d')}-{nowtime().replace(':', '')}"
		
		if frappe.db.exists("Temperature Log", {
			"log_number": self.log_number,
			"name": ("!=", self.name)
		}):
			frappe.throw(_("Log Number {0} already exists").format(self.log_number))

	def _validate_temperature(self):
		"""Validate temperature against acceptable range"""
		if self.min_temperature and self.max_temperature:
			if self.temperature < self.min_temperature or self.temperature > self.max_temperature:
				self.temperature_status = "Critical"
				self.excursion_flag = 1
			elif self.temperature < (self.min_temperature + 2) or self.temperature > (self.max_temperature - 2):
				self.temperature_status = "Warning"
			else:
				self.temperature_status = "Normal"

	def _determine_temperature_status(self):
		"""Determine temperature status based on temperature"""
		if self.temperature_status == "Normal":
			return
		
		# Check if cold chain required
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if batch.cold_chain_required:
				# For refrigerated (2-8°C)
				if batch.storage_temperature == "Refrigerated (2-8°C)":
					if self.temperature < 2 or self.temperature > 8:
						self.temperature_status = "Critical"
						self.excursion_flag = 1
					elif self.temperature < 3 or self.temperature > 7:
						self.temperature_status = "Warning"
				# For frozen (-20°C)
				elif batch.storage_temperature == "Frozen (-20°C)":
					if self.temperature > -15:
						self.temperature_status = "Critical"
						self.excursion_flag = 1
					elif self.temperature > -18:
						self.temperature_status = "Warning"

	def _check_excursion(self):
		"""Check if temperature excursion occurred"""
		if not self.excursion_flag:
			return

		previous_logs = frappe.get_all(
			"Temperature Log",
			{
				"batch_number": self.batch_number,
				"excursion_flag": 1,
				"log_date": self.log_date,
				"name": ("!=", self.name),
			},
			["log_time"],
			order_by="log_time DESC",
			limit=1,
		)

		if not previous_logs or not self.log_time:
			return

		from datetime import datetime, timedelta

		def _time_to_seconds(value):
			if isinstance(value, timedelta):
				return int(value.total_seconds())
			if isinstance(value, datetime):
				return value.hour * 3600 + value.minute * 60 + value.second
			if isinstance(value, str):
				parsed = datetime.strptime(value, "%H:%M:%S")
				return parsed.hour * 3600 + parsed.minute * 60 + parsed.second
			return 0

		duration = int((_time_to_seconds(self.log_time) - _time_to_seconds(previous_logs[0].log_time)) / 60)
		if duration > 0:
			self.excursion_duration = duration

	def _populate_batch_details(self):
		"""Populate batch details if batch is selected"""
		if self.batch_number:
			batch = frappe.get_doc("Pharma Batch", self.batch_number)
			if not self.item_code:
				self.item_code = batch.item_code
			if not self.warehouse:
				self.warehouse = batch.warehouse
			if not self.company:
				self.company = batch.company
			if not self.target_temperature:
				# Set target based on storage temperature
				if batch.storage_temperature == "Refrigerated (2-8°C)":
					self.target_temperature = 5
					self.min_temperature = 2
					self.max_temperature = 8
				elif batch.storage_temperature == "Frozen (-20°C)":
					self.target_temperature = -20
					self.min_temperature = -25
					self.max_temperature = -15

	def _create_excursion_if_needed(self):
		"""Create temperature excursion record if needed"""
		if self.excursion_flag:
			excursion = frappe.new_doc("Temperature Excursion")
			excursion.excursion_number = f"EXC-{now_datetime().strftime('%Y%m%d')}-{self.log_number}"
			excursion.excursion_date = self.log_date
			excursion.excursion_time = self.log_time
			excursion.batch_number = self.batch_number
			excursion.item_code = self.item_code
			excursion.warehouse = self.warehouse
			excursion.temperature = self.temperature
			excursion.temperature_unit = self.temperature_unit
			excursion.min_temperature = self.min_temperature
			excursion.max_temperature = self.max_temperature
			excursion.equipment_id = self.equipment_id
			excursion.equipment_type = self.equipment_type
			excursion.company = self.company
			excursion.duration_minutes = self.excursion_duration
			excursion.status = "Draft"
			excursion.insert()
			frappe.msgprint(_("Temperature Excursion {0} created").format(excursion.name))

	def _send_alert_if_needed(self):
		"""Send alert if temperature is critical"""
		if self.temperature_status == "Critical" and not self.alert_sent:
			# Log alert
			frappe.log_error(
				_("Critical Temperature Alert: {0}°C for Batch {1} in Warehouse {2}").format(
					self.temperature, self.batch_number, self.warehouse
				),
				"Cold Chain Alert"
			)
			self.alert_sent = 1
			self.alert_time = frappe.utils.now()

@frappe.whitelist()
def get_temperature_logs(batch_no, from_date=None, to_date=None):
	"""Get temperature logs for a batch"""
	filters = {"batch_number": batch_no}
	
	if from_date:
		filters["log_date"] = [">=", from_date]
	if to_date:
		if "log_date" in filters:
			filters["log_date"].append(["<=", to_date])
		else:
			filters["log_date"] = ["<=", to_date]
	
	logs = frappe.get_all("Temperature Log", filters,
		["name", "log_number", "log_date", "log_time", "temperature", "temperature_status", "excursion_flag"],
		order_by="log_date DESC, log_time DESC",
		limit=100)
	
	return logs

@frappe.whitelist()
def get_temperature_summary(batch_no):
	"""Get temperature summary for a batch"""
	from frappe.query_builder import DocType, functions as fn
	
	log = DocType("Temperature Log")
	
	query = (
		frappe.qb.from_(log)
		.select(
			fn.Avg(log.temperature).as_("avg_temp"),
			fn.Min(log.temperature).as_("min_temp"),
			fn.Max(log.temperature).as_("max_temp"),
			fn.Count(log.name).as_("total_logs")
		)
		.where(log.batch_number == batch_no)
	)
	
	result = query.run(as_dict=True)
	
	return result[0] if result else None
