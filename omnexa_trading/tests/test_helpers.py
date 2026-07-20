# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime, today

TEST_COMPANY_ABBR = "TPC"
TEST_COMPANY_NAME = "Test Pharma Company"


def ensure_test_company():
	"""Company autoname uses `abbr` as the document name."""
	if not frappe.db.exists("Company", TEST_COMPANY_ABBR):
		return frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": TEST_COMPANY_NAME,
				"abbr": TEST_COMPANY_ABBR,
				"country": "United Arab Emirates",
				"default_currency": "AED"
	}
		).insert()
	return frappe.get_doc("Company", TEST_COMPANY_ABBR)


def ensure_test_warehouse(company: str):
	warehouse_name = frappe.db.get_value(
		"Warehouse",
		{"warehouse_name": "Test Warehouse", "company": company
	},
		"name",
	)
	if warehouse_name:
		return frappe.get_doc("Warehouse", warehouse_name)
	return frappe.get_doc(
		{
			"doctype": "Warehouse",
			"warehouse_name": "Test Warehouse",
			"warehouse_code": "TW",
			"is_group": 0,
			"company": company
	}
	).insert()


def create_test_item(company: str):
	item_code = f"TEST-{now_datetime().strftime('%H%M%S%f')}"
	return frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": f"Test Pharma Item {item_code
	}",
			"item_group": "All Item Groups",
			"stock_uom": "Nos",
			"is_stock_item": 1,
			"company": company
	}
	).insert()


def item_link(item) -> str:
	"""Item links use document `name` (hash autoname in omnexa_accounting)."""
	return item.name


def create_test_customer(company: str):
	customer_code = f"CUST-{now_datetime().strftime('%H%M%S%f')}"
	return frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": f"Test Customer {customer_code
	}",
			"customer_code": customer_code,
			"customer_group": "All Customer Groups",
			"company": company
	}
	).insert()


def ensure_test_branch(company: str):
	branch_name = frappe.db.get_value(
		"Branch",
		{"company": company, "branch_code": "HO"
	},
		"name",
	)
	if branch_name:
		return frappe.get_doc("Branch", branch_name)
	return frappe.get_doc(
		{
			"doctype": "Branch",
			"branch_name": "Test Head Office",
			"branch_code": "HO",
			"company": company,
			"status": "Active",
			"is_head_office": 1
	}
	).insert()


def ensure_test_sales_representative(company: str, branch: str):
	rep_code = f"REP-{now_datetime().strftime('%H%M%S%f')}"
	return frappe.get_doc(
		{
			"doctype": "Trading Sales Representative",
			"rep_code": rep_code,
			"rep_name": f"Test Rep {rep_code
	}",
			"company": company,
			"branch": branch,
			"status": "Active"
	}
	).insert()


def ensure_test_customer_profile(company: str, branch: str, customer=None):
	customer_code = f"CP-{now_datetime().strftime('%H%M%S%f')}"
	return frappe.get_doc(
		{
			"doctype": "Customer Profile",
			"customer_code": customer_code,
			"customer_name": f"Test Profile {customer_code
	}",
			"customer_type": "Individual",
			"company": company,
			"branch": branch,
			"linked_customer": customer.name if customer else None,
			"status": "Active"
	}
	).insert()


def build_test_van_sales_invoice(
	company: str,
	branch: str,
	customer_profile,
	sales_rep,
	items: list,
	prescription_number: str | None = None,
):
	doc = {
		"doctype": "Trading Van Sales Invoice",
		"customer_profile": customer_profile.name,
		"posting_date": today(),
		"company": company,
		"branch": branch,
		"sales_representative": sales_rep.name,
		"payment_type": "Cash",
		"items": items
	}
	if prescription_number:
		doc["prescription_number"] = prescription_number

	normalized_items = []
	for row in items:
		row = dict(row)
		if "item_code" in row and "item" not in row:
			row["item"] = row.pop("item_code")
		normalized_items.append(row)
	doc["items"] = normalized_items

	return frappe.get_doc(doc)


def ensure_test_employee(company: str):
	employee_code = f"EMP-{now_datetime().strftime('%H%M%S%f')}"
	return frappe.get_doc(
		{
			"doctype": "Employee",
			"employee_code": employee_code,
			"employee_name": f"Test Inspector {employee_code
	}",
			"company": company,
			"status": "Active"
	}
	).insert()


def inspector_link(employee) -> str:
	return employee.name


def cleanup_doc(doc):
	if not doc:
		return
	try:
		if getattr(doc, "docstatus", 0) == 1:
			doc.cancel()
		else:
			doc.delete()
	except Exception:
		pass
