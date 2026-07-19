# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TradingDistributionOrder(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_assignments()
		self._set_totals()

	def on_submit(self):
		if self.status == "Planned":
			self.db_set("status", "In Transit", update_modified=False)

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def _validate_assignments(self):
		route = frappe.db.get_value(
			"Trading Route Plan",
			self.route_plan,
			["company", "branch", "sales_representative", "vehicle"],
			as_dict=True,
		)
		if not route:
			frappe.throw(_("Route Plan does not exist."), title=_("Route"))
		if route.company != self.company or route.branch != self.branch:
			frappe.throw(_("Route Plan must belong to same company and branch."), title=_("Route"))
		if route.sales_representative and self.sales_representative != route.sales_representative:
			frappe.throw(_("Sales Representative must match Route Plan assignment."), title=_("Route"))
		if route.vehicle and self.vehicle and self.vehicle != route.vehicle:
			frappe.throw(_("Vehicle must match Route Plan assignment."), title=_("Route"))

	def _set_totals(self):
		total_qty = 0.0
		total_amount = 0.0
		for row in self.items or []:
			if flt(row.qty) <= 0:
				frappe.throw(_("Row {0}: Qty must be greater than zero.").format(row.idx), title=_("Items"))
			row.amount = flt(flt(row.qty) * flt(row.rate), 2)
			total_qty += flt(row.qty)
			total_amount += flt(row.amount)
		self.total_qty = flt(total_qty, 2)
		self.total_amount = flt(total_amount, 2)

