# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Trading deployment phase hub — pharma distribution / import-export / POS retail."""

from __future__ import annotations

import frappe
from omnexa_trading.trading_pos_routes import count_pos_sales_today

PHASE_CACHE_KEY = "trading_demo_deployment_phase"

PHASE_DEFINITIONS: list[dict] = [
	{
		"id": "distribution",
		"icon": "🚚",
		"label_en": "Phase 1 – Pharma Distribution",
		"label_ar": "المرحلة 1 – التوزيع الدوائي",
		"summary_en": "Warehouses · van sales · routes · cold chain · dispatch",
		"summary_ar": "مستودعات · مبيعات ميدانية · مسارات · سلسلة باردة · تسليم",
		"portal_ids": [
			"warehouse-manager",
			"sales-director",
			"medical-rep",
			"area-manager",
			"sales-supervisor",
			"dispatch",
			"receiving",
			"store-keeper",
			"inventory-controller",
			"cold-chain-manager",
		],
		"company_abbr": "PTE",
		"branch_code": "HO",
	},
	{
		"id": "import_export",
		"icon": "🌍",
		"label_en": "Phase 2 – Import & Export",
		"label_ar": "المرحلة 2 – الاستيراد والتصدير",
		"summary_en": "Import licenses · export shipments · regulatory · quality",
		"summary_ar": "تراخيص استيراد · شحنات تصدير · تنظيمي · جودة",
		"portal_ids": [
			"import-manager",
			"export-manager",
			"regulatory-officer",
			"purchase-manager",
			"quality-manager",
		],
		"company_abbr": "PTE",
		"branch_code": "HO",
	},
	{
		"id": "pos_retail",
		"icon": "🛒",
		"label_en": "Phase 3 – POS & Retail",
		"label_ar": "المرحلة 3 – نقاط البيع والتجزئة",
		"summary_en": "Point of sale · cashier · customer service · treasury",
		"summary_ar": "نقاط البيع · أمين الصندوق · خدمة العملاء · الخزينة",
		"portal_ids": [
			"cashier",
			"customer-service",
			"treasury",
			"chief-accountant",
			"finance-director",
		],
		"company_abbr": "PTE",
		"branch_code": "HO",
	},
]


def _resolve_company_branch(phase: dict) -> tuple[str, str]:
	company = frappe.db.get_value("Company", {"abbr": phase.get("company_abbr")}, "name")
	if not company:
		company = frappe.db.get_value("Company", {}, "name")
	branch = ""
	if company:
		branch = (
			frappe.db.get_value("Branch", {"company": company, "branch_code": phase.get("branch_code")}, "name")
			or frappe.db.get_value("Branch", {"company": company}, "name")
			or ""
		)
	return company or "", branch or ""


def _branch_stats(company: str, branch: str) -> dict:
	stats = {
		"customers": 0,
		"orders": 0,
		"batches": 0,
		"pos_sales": 0,
	}
	if frappe.db.exists("DocType", "Customer"):
		stats["customers"] = frappe.db.count("Customer")
	if frappe.db.exists("DocType", "Sales Order"):
		stats["orders"] = frappe.db.count("Sales Order", {"docstatus": 1})
	if frappe.db.exists("DocType", "Pharma Batch"):
		stats["batches"] = frappe.db.count("Pharma Batch")
	if frappe.db.exists("DocType", "POS Invoice") or frappe.db.has_column("Sales Invoice", "is_pos"):
		stats["pos_sales"] = count_pos_sales_today()
	return stats


def _portal_rows(portal_ids: set[str]) -> list[dict]:
	from omnexa_trading.trading_portal_catalog import get_portal_catalog

	rows = []
	for portal in get_portal_catalog(include_missing=0):
		pid = portal.get("id") or portal.get("key")
		if pid in portal_ids:
			rows.append(portal)
	return rows


@frappe.whitelist()
def get_deployment_phases_dashboard() -> dict:
	active_phase = frappe.cache().get_value(PHASE_CACHE_KEY) or ""
	default_company = frappe.defaults.get_user_default("Company") or ""
	default_branch = frappe.defaults.get_user_default("Branch") or ""

	phases = []
	for phase in PHASE_DEFINITIONS:
		company, branch = _resolve_company_branch(phase)
		ready = bool(company and (branch or frappe.db.count("Branch", {"company": company}) >= 0))
		stats = _branch_stats(company, branch) if company else {}
		portal_ids = set(phase.get("portal_ids") or [])
		portals = _portal_rows(portal_ids)
		phases.append({
			**phase,
			"company": company,
			"branch": branch,
			"ready": ready,
			"active": active_phase == phase["id"],
			"stats": stats,
			"portals": portals,
			"portal_count": len(portals),
			"pos_url": "/app/retail-pos",
		})

	return {
		"ok": True,
		"active_phase": active_phase,
		"default_company": default_company,
		"default_branch": default_branch,
		"phases": phases,
	}


@frappe.whitelist()
def set_deployment_phase_context(phase_id: str) -> dict:
	frappe.only_for("System Manager")
	valid = {p["id"] for p in PHASE_DEFINITIONS}
	if phase_id not in valid:
		frappe.throw(f"Unknown phase: {phase_id}")
	phase = next(p for p in PHASE_DEFINITIONS if p["id"] == phase_id)
	company, branch = _resolve_company_branch(phase)
	if company:
		frappe.defaults.set_user_default("Company", company)
	if branch:
		frappe.defaults.set_user_default("Branch", branch)
	frappe.cache().set_value(PHASE_CACHE_KEY, phase_id)
	return {"ok": True, "phase_id": phase_id, "company": company, "branch": branch}


@frappe.whitelist()
def activate_deployment_phase(phase_id: str, force: int = 1) -> dict:
	frappe.only_for("System Manager")
	from omnexa_trading.omnexa_trading.data.pharma_demo_setup import run_pharma_demo_setup

	result = run_pharma_demo_setup()
	if not result:
		frappe.throw("Pharma demo setup failed. Check Error Log for details.")
	set_deployment_phase_context(phase_id)
	return {
		"ok": True,
		"phase_id": phase_id,
		"message": f"Trading phase {phase_id} activated",
		"result": result,
	}
