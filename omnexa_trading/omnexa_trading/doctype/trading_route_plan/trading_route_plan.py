# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingRoutePlan(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_assignments()
		self._validate_stops()
		self._validate_distance()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_assignments(self):
		rep_branch = frappe.db.get_value("Trading Sales Representative", self.sales_representative, "branch")
		if rep_branch and rep_branch != self.branch:
			frappe.throw(_("Sales Representative must belong to same branch."), title=_("Route"))
		if self.vehicle:
			vehicle_branch = frappe.db.get_value("Trading Vehicle", self.vehicle, "branch")
			if vehicle_branch and vehicle_branch != self.branch:
				frappe.throw(_("Vehicle must belong to same branch."), title=_("Route"))

	def _validate_stops(self):
		seen = set()
		for row in self.stops or []:
			key = row.stop_sequence
			if key in seen:
				frappe.throw(_("Duplicate stop sequence in route plan."), title=_("Route"))
			seen.add(key)

	def _validate_distance(self):
		if flt(self.planned_distance_km) < 0 or flt(self.actual_distance_km) < 0:
			frappe.throw(_("Distances cannot be negative."), title=_("Route"))

