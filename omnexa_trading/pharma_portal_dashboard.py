# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Role portal dashboard — work queue, tasks, approvals, KPIs per pro.md spec."""

from __future__ import annotations

import frappe
from frappe.utils import flt, nowdate, today

from omnexa_trading.pharma_portal_catalog import get_portal_by_key
from omnexa_trading.trading_pos_routes import count_pos_sales_today, get_pos_invoice_list_route


def _safe_count(doctype: str, filters: dict | None = None) -> int:
	try:
		if not frappe.db.exists("DocType", doctype):
			return 0
		return frappe.db.count(doctype, filters or {})
	except Exception:
		return 0


def _safe_list(doctype: str, fields: list[str], filters: dict | None = None, limit: int = 8) -> list[dict]:
	try:
		if not frappe.db.exists("DocType", doctype):
			return []
		return frappe.get_all(doctype, fields=fields, filters=filters or {}, limit=limit, order_by="modified desc")
	except Exception:
		return []


def _kpi(label_en: str, label_ar: str, value, icon: str = "📊") -> dict:
	return {"title_en": label_en, "title_ar": label_ar, "title": label_en, "value": value, "icon": icon}


def _action(label_en: str, label_ar: str, route: str, icon: str = "⚡") -> dict:
	return {"label_en": label_en, "label_ar": label_ar, "route": route, "icon": icon}


_ROLE_DASHBOARD_BUILDERS: dict[str, callable] = {}


def _register(role_key: str):
	def decorator(fn):
		_ROLE_DASHBOARD_BUILDERS[role_key] = fn
		return fn

	return decorator


@_register("ceo")
@_register("chairman")
@_register("executive-dashboard")
@_register("general-manager")
@_register("commercial-director")
def _executive_dashboard(_portal: dict) -> dict:
	pos_today = count_pos_sales_today()
	pos_profiles = _safe_count("POS Profile")
	return {
		"kpis": [
			_kpi("Open Sales Orders", "أوامر مبيعات مفتوحة", _safe_count("Sales Order", {"docstatus": 1, "status": ["!=", "Completed"]}), "🛍️"),
			_kpi("POS Sales Today", "مبيعات نقاط البيع اليوم", pos_today, "🛒"),
			_kpi("POS Profiles", "نقاط البيع النشطة", pos_profiles, "💵"),
			_kpi("Open CAPAs", "CAPA مفتوحة", _safe_count("CAPA", {"status": ["!=", "Closed"]}), "🔧"),
			_kpi("Active Recalls", "استدعاءات نشطة", _safe_count("Pharma Product Recall", {"status": ["!=", "Closed"]}), "🔄"),
		],
		"work_queue": _safe_list("Sales Order", ["name", "customer", "status"], {"docstatus": 1}, 6),
		"pending_tasks": _safe_list("ToDo", ["name", "description", "status"], {"status": "Open"}, 6),
		"approvals": _safe_list("Purchase Order", ["name", "supplier", "status"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("Point of Sale", "نقطة البيع", "/app/retail-pos", "🛒"),
			_action("POS Invoices", "فواتير نقاط البيع", get_pos_invoice_list_route(), "🧾"),
			_action("POS Z Reconciliation", "تسوية نقاط البيع", "/app/query-report/POS Z Report Reconciliation", "📊"),
			_action("Sales Summary", "ملخص المبيعات", "/app/query-report/Trading Sales Summary", "📈"),
		],
		"charts": [
			{"id": "revenue", "title_en": "Revenue Trend", "title_ar": "اتجاه الإيرادات", "type": "line"},
			{"id": "pos", "title_en": "POS Sales", "title_ar": "مبيعات نقاط البيع", "type": "bar"},
		],
		"notifications": ["approval_request", "compliance_alert", "recall_alert", "pos_reconciliation"],
	}


@_register("warehouse-manager")
@_register("store-keeper")
@_register("inventory-controller")
def _warehouse_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Stock Entries Today", "حركات اليوم", _safe_count("Stock Entry", {"posting_date": today()}), "📦"),
			_kpi("Open Deliveries", "تسليمات مفتوحة", _safe_count("Delivery Note", {"docstatus": 1, "status": ["!=", "Completed"]}), "🚚"),
			_kpi("Pharma Batches", "دفعات دوائية", _safe_count("Pharma Batch"), "💊"),
			_kpi("Temp Excursions", "انحرافات حرارة", _safe_count("Temperature Excursion", {"status": "Open"}), "🌡️"),
		],
		"work_queue": _safe_list("Stock Entry", ["name", "stock_entry_type", "docstatus"], {"docstatus": ["<", 2]}, 6),
		"pending_tasks": _safe_list("Delivery Note", ["name", "customer", "status"], {"docstatus": 0}, 5),
		"approvals": _safe_list("Purchase Receipt", ["name", "supplier", "status"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("New Stock Entry", "حركة مخزون", "/app/stock-entry/new", "📦"),
			_action("Delivery Notes", "إذن تسليم", "/app/List/Delivery Note", "🚚"),
			_action("Pharma Batches", "الدفعات", "/app/List/Pharma Batch", "💊"),
		],
		"charts": [{"id": "stock", "title_en": "Stock Movement", "title_ar": "حركة المخزون", "type": "bar"}],
		"notifications": ["low_stock", "expiry_alert", "temperature_alert"],
	}


@_register("dispatch")
def _dispatch_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Pending Dispatch", "تسليم معلق", _safe_count("Delivery Note", {"docstatus": 0}), "🚚"),
			_kpi("In Transit", "قيد النقل", _safe_count("Delivery Note", {"docstatus": 1, "status": "To Bill"}), "📦"),
			_kpi("Distribution Orders", "أوامر توزيع", _safe_count("Trading Distribution Order", {"docstatus": 1}), "📋"),
			_kpi("Cold Shipments", "شحنات باردة", _safe_count("Pharma Batch", {"storage_condition": ["like", "%Cold%"]}), "❄️"),
		],
		"work_queue": _safe_list("Delivery Note", ["name", "customer", "status"], {"docstatus": ["<", 2]}, 8),
		"pending_tasks": _safe_list("Trading Distribution Order", ["name", "customer", "status"], {"docstatus": 0}, 6),
		"approvals": [],
		"quick_actions": [
			_action("Create Delivery", "إذن تسليم", "/app/delivery-note/new", "🚚"),
			_action("Distribution Orders", "أوامر التوزيع", "/app/List/Trading Distribution Order", "📋"),
		],
		"charts": [{"id": "dispatch", "title_en": "Dispatch Volume", "title_ar": "حجم التسليم", "type": "bar"}],
		"notifications": ["dispatch_delay", "cold_chain_alert"],
	}


@_register("purchase-manager")
@_register("import-manager")
@_register("receiving")
def _receiving_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Pending Receipts", "استلام معلق", _safe_count("Purchase Receipt", {"docstatus": 0}), "📥"),
			_kpi("QC Pending", "فحص معلق", _safe_count("Pharma Quality Inspection", {"status": "Pending"}), "🔬"),
			_kpi("Open POs", "أوامر شراء", _safe_count("Purchase Order", {"docstatus": 1, "status": ["!=", "Completed"]}), "🛒"),
			_kpi("Import Shipments", "شحنات استيراد", _safe_count("Pharma Import License", {"status": "Active"}), "📥"),
		],
		"work_queue": _safe_list("Purchase Receipt", ["name", "supplier", "status"], {"docstatus": ["<", 2]}, 8),
		"pending_tasks": _safe_list("Pharma Quality Inspection", ["name", "batch_no", "status"], {"status": "Pending"}, 6),
		"approvals": _safe_list("Purchase Order", ["name", "supplier", "status"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("Receive Goods", "استلام بضائع", "/app/purchase-receipt/new", "📥"),
			_action("Quality Inspection", "فحص جودة", "/app/pharma-quality-inspection/new", "🔬"),
		],
		"charts": [{"id": "receiving", "title_en": "Receiving Volume", "title_ar": "حجم الاستلام", "type": "line"}],
		"notifications": ["receipt_pending", "qc_required"],
	}


@_register("export-manager")
@_register("sales-director")
@_register("area-manager")
@_register("sales-supervisor")
@_register("medical-rep")
def _sales_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Open Sales Orders", "أوامر مبيعات", _safe_count("Sales Order", {"docstatus": 1}), "🛍️"),
			_kpi("Van Invoices Today", "فواتير اليوم", _safe_count("Trading Van Sales Invoice", {"posting_date": today()}), "🚐"),
			_kpi("Active Routes", "مسارات نشطة", _safe_count("Trading Route Plan", {"docstatus": 1}), "🗺️"),
			_kpi("Customers", "العملاء", _safe_count("Customer"), "👥"),
		],
		"work_queue": _safe_list("Sales Order", ["name", "customer", "status"], {"docstatus": ["<", 2]}, 6),
		"pending_tasks": _safe_list("Trading Route Plan", ["name", "route_date", "status"], {"docstatus": 0}, 5),
		"approvals": _safe_list("Trading Tender", ["name", "customer", "status"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("New Sales Order", "أمر مبيعات", "/app/sales-order/new", "🛍️"),
			_action("Van Sales", "مبيعات ميدانية", "/app/trading-van-sales-pwa", "🚐"),
			_action("Route Plans", "خطط المسارات", "/app/List/Trading Route Plan", "🗺️"),
		],
		"charts": [{"id": "sales", "title_en": "Sales Trend", "title_ar": "اتجاه المبيعات", "type": "line"}],
		"notifications": ["target_alert", "credit_limit", "route_reminder"],
	}


@_register("finance-director")
@_register("chief-accountant")
@_register("treasury")
@_register("cashier")
def _finance_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Unpaid Invoices", "فواتير غير مدفوعة", _safe_count("Sales Invoice", {"docstatus": 1, "outstanding_amount": [">", 0]}), "🧾"),
			_kpi("Payments Today", "مدفوعات اليوم", _safe_count("Payment Entry", {"posting_date": today()}), "💳"),
			_kpi("Open Journals", "قيود مفتوحة", _safe_count("Journal Entry", {"docstatus": 0}), "📒"),
			_kpi("Installment Contracts", "عقود تقسيط", _safe_count("Trading Installment Contract", {"docstatus": 1}), "💰"),
		],
		"work_queue": _safe_list("Sales Invoice", ["name", "customer", "outstanding_amount"], {"docstatus": 1, "outstanding_amount": [">", 0]}, 6),
		"pending_tasks": _safe_list("Payment Entry", ["name", "party", "paid_amount"], {"docstatus": 0}, 5),
		"approvals": _safe_list("Journal Entry", ["name", "voucher_type", "total_debit"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("Payment Entry", "سند قبض/صرف", "/app/payment-entry/new", "💳"),
			_action("Sales Summary", "ملخص المبيعات", "/app/query-report/Trading Sales Summary", "📈"),
			_action("General Ledger", "دفتر الأستاذ", "/app/query-report/General Ledger", "📊"),
		],
		"charts": [{"id": "cashflow", "title_en": "Cash Flow", "title_ar": "التدفق النقدي", "type": "area"}],
		"notifications": ["payment_due", "credit_alert", "reconciliation"],
	}


@_register("customer-service")
def _customer_service_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Open Issues", "بلاغات مفتوحة", _safe_count("Issue", {"status": "Open"}), "🎫"),
			_kpi("Customers", "العملاء", _safe_count("Customer"), "👥"),
			_kpi("Open Recalls", "استدعاءات", _safe_count("Pharma Product Recall", {"status": ["!=", "Closed"]}), "🔄"),
			_kpi("Pending Returns", "مرتجعات", _safe_count("Delivery Note", {"is_return": 1, "docstatus": 0}), "↩️"),
		],
		"work_queue": _safe_list("Issue", ["name", "subject", "status"], {"status": "Open"}, 8),
		"pending_tasks": _safe_list("Customer", ["name", "customer_name", "customer_group"], {}, 5),
		"approvals": [],
		"quick_actions": [
			_action("Customers", "العملاء", "/app/List/Customer", "👥"),
			_action("New Issue", "بلاغ جديد", "/app/issue/new", "🎫"),
			_action("Product Recall", "استدعاء", "/app/List/Pharma Product Recall", "🔄"),
		],
		"charts": [{"id": "tickets", "title_en": "Ticket Volume", "title_ar": "حجم البلاغات", "type": "bar"}],
		"notifications": ["new_ticket", "customer_complaint", "recall_notice"],
	}


@_register("hr-director")
def _hr_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Employees", "الموظفون", _safe_count("Employee", {"status": "Active"}), "👥"),
			_kpi("Training Due", "تدريب مستحق", _safe_count("Training Record", {"status": "Scheduled"}), "🎓"),
			_kpi("Open CAPAs", "CAPA HR", _safe_count("CAPA", {"status": ["!=", "Closed"]}), "🔧"),
			_kpi("Sales Reps", "مندوبين", _safe_count("Trading Sales Representative"), "🚐"),
		],
		"work_queue": _safe_list("Training Record", ["name", "training_title", "status"], {"status": ["!=", "Completed"]}, 6),
		"pending_tasks": _safe_list("Employee", ["name", "employee_name", "department"], {"status": "Active"}, 5),
		"approvals": [],
		"quick_actions": [
			_action("Employees", "الموظفون", "/app/List/Employee", "👥"),
			_action("Training Records", "التدريب", "/app/List/Training Record", "🎓"),
			_action("Sales Reps", "المندوبين", "/app/List/Trading Sales Representative", "🚐"),
		],
		"charts": [{"id": "training", "title_en": "Training Compliance", "title_ar": "امتثال التدريب", "type": "donut"}],
		"notifications": ["training_due", "certification_expiry"],
	}


@_register("quality-manager")
@_register("cold-chain-manager")
@_register("regulatory-officer")
@_register("auditor")
def _compliance_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Open CAPAs", "CAPA مفتوحة", _safe_count("CAPA", {"status": ["!=", "Closed"]}), "🔧"),
			_kpi("Open Deviations", "انحرافات", _safe_count("Deviation", {"status": ["!=", "Closed"]}), "⚠️"),
			_kpi("Pending Inspections", "فحوصات", _safe_count("Pharma Quality Inspection", {"status": "Pending"}), "🔬"),
			_kpi("Active Recalls", "استدعاءات", _safe_count("Pharma Product Recall", {"status": ["!=", "Closed"]}), "🔄"),
		],
		"work_queue": _safe_list("CAPA", ["name", "status"], {"status": ["!=", "Closed"]}, 6),
		"pending_tasks": _safe_list("Deviation", ["name", "status"], {"status": ["!=", "Closed"]}, 6),
		"approvals": _safe_list("Pharma Regulatory Approval", ["name", "status"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("CAPA", "CAPA", "/app/List/CAPA", "🔧"),
			_action("Quality Inspection", "فحص جودة", "/app/List/Pharma Quality Inspection", "🔬"),
			_action("Audit Log", "سجل التدقيق", "/app/List/Audit Log", "📋"),
		],
		"charts": [{"id": "compliance", "title_en": "Compliance Trend", "title_ar": "اتجاه الامتثال", "type": "line"}],
		"notifications": ["capa_due", "deviation_alert", "recall_alert"],
	}


@_register("operations-director")
@_register("workcenter")
def _operations_dashboard(_portal: dict) -> dict:
	return {
		"kpis": [
			_kpi("Open Orders", "أوامر مفتوحة", _safe_count("Sales Order", {"docstatus": 1}), "🛍️"),
			_kpi("Stock Movements", "حركات مخزون", _safe_count("Stock Entry", {"docstatus": ["<", 2]}), "📦"),
			_kpi("Pending POs", "مشتريات", _safe_count("Purchase Order", {"docstatus": 0}), "🛒"),
			_kpi("Distribution Orders", "توزيع", _safe_count("Trading Distribution Order", {"docstatus": 1}), "📋"),
		],
		"work_queue": _safe_list("Trading Distribution Order", ["name", "customer", "status"], {"docstatus": ["<", 2]}, 6),
		"pending_tasks": _safe_list("Stock Entry", ["name", "stock_entry_type"], {"docstatus": 0}, 6),
		"approvals": _safe_list("Purchase Order", ["name", "supplier"], {"docstatus": 0}, 5),
		"quick_actions": [
			_action("Workcenter", "مركز العمل", "/app/trading-workcenter", "🏢"),
			_action("Operations", "العمليات", "/app/trading-operations-director", "⚙️"),
			_action("Distribution", "التوزيع", "/app/List/Trading Distribution Order", "📋"),
		],
		"charts": [{"id": "ops", "title_en": "Operations Volume", "title_ar": "حجم العمليات", "type": "bar"}],
		"notifications": ["ops_delay", "stock_alert"],
	}


def _default_dashboard(portal: dict) -> dict:
	key = portal.get("key", "")
	return {
		"kpis": [
			_kpi("Pending Documents", "مستندات معلقة", _safe_count("ToDo", {"status": "Open"}), "📋"),
			_kpi("Open Tasks", "مهام", _safe_count("ToDo", {"status": "Open"}), "✅"),
			_kpi("Notifications", "إشعارات", len(frappe.get_all("Notification Log", limit=10)), "🔔"),
			_kpi("Today", "اليوم", nowdate(), "📅"),
		],
		"work_queue": _safe_list("ToDo", ["name", "description", "status"], {"status": "Open"}, 6),
		"pending_tasks": _safe_list("ToDo", ["name", "description", "date"], {"status": "Open"}, 6),
		"approvals": [],
		"quick_actions": [
			_action("Workcenter", "مركز العمل", portal.get("route", "/app/trading-workcenter"), "🏢"),
		],
		"charts": [{"id": key, "title_en": "Activity", "title_ar": "النشاط", "type": "line"}],
		"notifications": ["system_alert"],
	}


@frappe.whitelist()
def get_role_portal_dashboard(role_key: str) -> dict:
	portal = get_portal_by_key(role_key)
	if not portal:
		frappe.throw(f"Unknown role portal: {role_key}")

	builder = _ROLE_DASHBOARD_BUILDERS.get(role_key) or _ROLE_DASHBOARD_BUILDERS.get(portal["key"])
	data = (builder or _default_dashboard)(portal)
	return {
		"role_key": role_key,
		"portal": {"key": portal["key"], "label_en": portal["label_en"], "label_ar": portal["label_ar"]},
		**data,
	}
