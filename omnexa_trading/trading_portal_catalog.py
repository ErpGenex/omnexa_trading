# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Trading portal catalog — delegates to pharma SSOT when available."""

from __future__ import annotations

import frappe
from frappe.utils import cint

from omnexa_trading.pharma_portal_catalog import (
	CATEGORY_LABELS as PHARMA_CATEGORY_LABELS,
	get_grouped_pharma_portal_catalog,
	get_pharma_portal_catalog,
)

# Legacy catalog kept for backward compatibility
LEGACY_PORTAL_CATALOG: list[dict] = [
	{"id": "workcenter", "route": "/app/trading-workcenter", "page": "trading-workcenter", "icon": "🏢", "category": "admin", "roles": ["System Manager", "Company Admin"], "label_ar": "مركز العمل", "label_en": "Workcenter"},
	{"id": "executive", "route": "/app/trading-executive-dashboard", "page": "trading-executive-dashboard", "icon": "📊", "category": "management", "roles": ["Company Admin", "Sales Manager"], "label_ar": "لوحة الإدارة التنفيذية", "label_en": "Executive Dashboard"},
	{"id": "operations", "route": "/app/trading-operations-desk", "page": "trading-operations-desk", "icon": "⚙️", "category": "operations", "roles": ["Sales User", "Stock User", "Purchase User"], "label_ar": "مكتب العمليات", "label_en": "Operations Desk"},
	{"id": "finance", "route": "/app/trading-finance-desk", "page": "trading-finance-desk", "icon": "💰", "category": "finance", "roles": ["Accounts User", "Accounts Manager"], "label_ar": "مكتب المالية", "label_en": "Finance Desk"},
	{"id": "customer", "route": "/app/trading-customer-portal", "page": "trading-customer-portal", "icon": "👤", "category": "customer", "roles": ["Customer", "Trading Customer Portal"], "label_ar": "بوابة العميل", "label_en": "Customer Portal"},
	{"id": "analytics", "route": "/app/trading-analytics-dashboard", "page": "trading-analytics-dashboard", "icon": "📈", "category": "management", "roles": ["Sales Manager", "Company Admin"], "label_ar": "لوحة التحليلات", "label_en": "Analytics Dashboard"},
	{"id": "van-sales", "route": "/app/trading-van-sales-pwa", "page": "trading-van-sales-pwa", "icon": "🚚", "category": "field", "roles": ["Sales User", "Stock User"], "label_ar": "مبيعات المندوبين", "label_en": "Van Sales PWA"},
]

CATEGORY_LABELS = PHARMA_CATEGORY_LABELS


def _page_exists(page_name: str) -> bool:
	return bool(frappe.db.exists("Page", page_name))


def _get_trading_multi_portal_context() -> dict:
	try:
		from omnexa_core.multi_portal.portal_factory import PortalFactory
		from omnexa_core.multi_portal.serialization import to_serializable
		from omnexa_core.multi_portal.user_resolver import get_user_portal_role
		from omnexa_trading.pharma_portal_catalog import get_portal_for_user

		portal = get_portal_for_user()
		role = get_user_portal_role(frappe.session.user, "commerce")
		if not role:
			return {"enabled": False}
		return {
			"enabled": True,
			"application": "commerce",
			"alias": "trading",
			"role": role,
			"pharma_portal": portal,
			"portal": to_serializable(PortalFactory().create_portal("commerce", role)),
		}
	except Exception:
		return {"enabled": False}


def _normalize_pharma_portal(row: dict) -> dict:
	return {
		"id": row.get("key") or row.get("id"),
		"route": row.get("route"),
		"page": row.get("page"),
		"icon": row.get("icon"),
		"category": row.get("category"),
		"roles": row.get("roles", []),
		"label_ar": row.get("label_ar"),
		"label_en": row.get("label_en"),
		"role_ar": row.get("role_ar"),
		"role_en": row.get("role_en"),
		"exists": row.get("exists", _page_exists(row.get("page", ""))),
	}


@frappe.whitelist()
def get_portal_catalog(include_missing: int = 0) -> list[dict]:
	pharma = get_pharma_portal_catalog(include_missing=cint(include_missing))
	if pharma:
		return [_normalize_pharma_portal(row) for row in pharma]
	out = []
	for row in LEGACY_PORTAL_CATALOG:
		item = dict(row)
		item["exists"] = _page_exists(item["page"])
		if item["exists"] or cint(include_missing):
			out.append(item)
	return out


@frappe.whitelist()
def get_grouped_portal_catalog(include_missing: int = 0) -> list[dict]:
	pharma_groups = get_grouped_pharma_portal_catalog(include_missing=cint(include_missing))
	if pharma_groups:
		result = []
		for group in pharma_groups:
			result.append({
				"category": group["category"],
				"label_ar": group["label_ar"],
				"label_en": group["label_en"],
				"portals": [_normalize_pharma_portal(p) for p in group.get("portals", [])],
			})
		return result
	groups: dict[str, list] = {}
	for row in get_portal_catalog(include_missing=cint(include_missing)):
		groups.setdefault(row["category"], []).append(row)
	result = []
	for cat, portals in groups.items():
		labels = CATEGORY_LABELS.get(cat, {"ar": cat, "en": cat})
		result.append({"category": cat, "label_ar": labels["ar"], "label_en": labels["en"], "portals": portals})
	return result


@frappe.whitelist()
def get_workcenter_context() -> dict:
	from omnexa_core.omnexa_core.app_logo_registry import get_logo_url

	groups = get_grouped_portal_catalog(include_missing=0)
	is_admin = frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
	company = frappe.defaults.get_user_default("Company") or ""

	customers = items = sales = 0
	if frappe.db.exists("DocType", "Customer"):
		filters = {"company": company} if company else {}
		customers = frappe.db.count("Customer", filters) if filters else frappe.db.count("Customer")
	if frappe.db.exists("DocType", "Item"):
		items = frappe.db.count("Item", {"disabled": 0})
	if frappe.db.exists("DocType", "Sales Invoice"):
		filters = {"company": company, "docstatus": 1} if company else {"docstatus": 1}
		sales = frappe.db.count("Sales Invoice", filters)

	credentials = {"password": "", "users": []}
	if is_admin:
		from omnexa_trading.api.trading_role_demo import _demo_credentials_payload

		credentials = _demo_credentials_payload()

	return {
		"grouped_portals": groups,
		"logo_url": get_logo_url("omnexa_trading"),
		"is_admin": is_admin,
		"multi_portal": _get_trading_multi_portal_context(),
		"pharma_portal_count": sum(len(g.get("portals") or []) for g in groups),
		"demo": {
			"can_seed": is_admin,
			"password": credentials.get("password"),
			"credentials": credentials,
		},
		"kpis": [
			{"label_ar": "العملاء", "label_en": "Customers", "value": customers},
			{"label_ar": "الأصناف", "label_en": "Items", "value": items},
			{"label_ar": "فواتير المبيعات", "label_en": "Sales Invoices", "value": sales},
			{"label_ar": "بوابات Pharma", "label_en": "Pharma Portals", "value": sum(len(g.get("portals") or []) for g in groups)},
		],
	}


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""Sector KPI preview bridge — re-export for gap register / BI integration."""
	from omnexa_trading.api import preview_sector_kpi as _preview

	return _preview(scenario=scenario, params=params)
