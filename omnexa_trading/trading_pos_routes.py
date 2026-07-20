# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""POS route helpers — resolve list/form URLs when ERPNext POS doctypes are absent."""

from __future__ import annotations

import frappe


def _has_doctype(name: str) -> bool:
	return bool(frappe.db.exists("DocType", name))


def _list_route(doctype: str) -> str:
	slug = frappe.scrub(doctype)
	return f"/app/List/{doctype}" if _has_doctype(doctype) else f"/app/{slug}"


def _redirect_target(doctype: str, *, fallback_doctype: str | None = None, fallback_filters: dict | None = None, fallback_page: str | None = None) -> dict:
	if _has_doctype(doctype):
		return {"kind": "list", "doctype": doctype, "filters": {}
	}
	if fallback_doctype and _has_doctype(fallback_doctype):
		return {"kind": "list", "doctype": fallback_doctype, "filters": fallback_filters or {}
	}
	if fallback_page:
		return {"kind": "page", "page": fallback_page
	}
	return {"kind": "page", "page": "retail-pos"
	}


def get_pos_invoice_list_route() -> str:
	if _has_doctype("POS Invoice"):
		return "/app/List/POS Invoice"
	return "/app/sales-invoice?is_pos=1"


def get_pos_invoice_new_route() -> str:
	if _has_doctype("POS Invoice"):
		return "/app/pos-invoice/new"
	return "/app/retail-pos"


def get_pos_opening_entry_route() -> str:
	if _has_doctype("POS Opening Entry"):
		return "/app/List/POS Opening Entry"
	if _has_doctype("POS Profile"):
		return "/app/List/POS Profile"
	return "/app/retail-pos"


def get_pos_closing_entry_route() -> str:
	if _has_doctype("POS Closing Entry"):
		return "/app/List/POS Closing Entry"
	if frappe.db.exists("Report", "POS Z Report Reconciliation"):
		return "/app/query-report/POS Z Report Reconciliation"
	if _has_doctype("Payment Entry"):
		return "/app/List/Payment Entry"
	return "/app/retail-pos"


@frappe.whitelist()
def get_pos_invoice_redirect() -> dict:
	return _redirect_target(
		"POS Invoice",
		fallback_doctype="Sales Invoice",
		fallback_filters={"is_pos": 1
	},
		fallback_page="retail-pos",
	)


@frappe.whitelist()
def get_pos_opening_entry_redirect() -> dict:
	return _redirect_target(
		"POS Opening Entry",
		fallback_doctype="POS Profile",
		fallback_page="retail-pos",
	)


@frappe.whitelist()
def get_pos_closing_entry_redirect() -> dict:
	if _has_doctype("POS Closing Entry"):
		return {"kind": "list", "doctype": "POS Closing Entry", "filters": {}
	}
	if frappe.db.exists("Report", "POS Z Report Reconciliation"):
		return {"kind": "report", "report": "POS Z Report Reconciliation"
	}
	if _has_doctype("Payment Entry"):
		return {"kind": "list", "doctype": "Payment Entry", "filters": {}
	}
	return {"kind": "page", "page": "retail-pos"
	}


def count_pos_sales_today() -> int:
	from frappe.utils import today

	posting_date = today()
	if _has_doctype("POS Invoice"):
		return frappe.db.count("POS Invoice", {"posting_date": posting_date, "docstatus": 1
	})
	if frappe.db.has_column("Sales Invoice", "is_pos"):
		return frappe.db.count(
			"Sales Invoice",
			{"posting_date": posting_date, "docstatus": 1, "is_pos": 1
	},
		)
	return 0
