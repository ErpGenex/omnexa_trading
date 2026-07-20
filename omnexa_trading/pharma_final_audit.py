# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Final audit — pharma trading demo readiness for global import/export distributor."""

from __future__ import annotations

import frappe

from omnexa_trading.pharma_evaluation import get_pharma_evaluation_score
from omnexa_trading.pharma_portal_catalog import PHARMA_ROLE_PORTALS, PRO_MD_REQUIRED_ROLE_KEYS, get_portal_by_key
from omnexa_trading.trading_gap_register import get_gap_status
from omnexa_trading.trading_global_benchmark import get_global_trading_score

LEGACY_SIDEBAR_WORKSPACES = (
	"إدارة المستودعات - Warehouse Management",
	"Pharma Warehouse Management",
)

DEMO_COMPANY = "PharmaTrade Egypt Ltd."

DEMO_CHECKS = (
	("pharma_batch", "Pharma Batch"),
	("import_license", "Pharma Import License"),
	("export_shipment", "Pharma Export Shipment"),
	("drug_registration", "Pharma Drug Registration"),
	("quality_inspection", "Pharma Quality Inspection"),
	("temperature_log", "Temperature Log"),
	("sales_order", "Sales Order"),
	("purchase_order", "Purchase Order"),
)


def _resolve_demo_company() -> str | None:
	if frappe.db.exists("Company", DEMO_COMPANY):
		return DEMO_COMPANY
	pte = frappe.db.get_value("Company", {"abbr": "PTE"
	}, "name")
	return pte or frappe.db.get_value("Company", {}, "name")


def _sidebar_clean() -> dict:
	legacy_found = [name for name in LEGACY_SIDEBAR_WORKSPACES if frappe.db.exists("Workspace", name)]
	return {
		"clean": not legacy_found,
		"legacy_workspaces": legacy_found
	}


def _demo_company_ready() -> dict:
	company_name = _resolve_demo_company()
	company_exists = bool(company_name)
	branch_count = frappe.db.count("Branch", {"company": company_name
	}) if company_exists else 0
	user_count = frappe.db.count("User", {"enabled": 1, "name": ["like", "%pharmatrade-egypt.com%"]})
	return {
		"company": company_name or DEMO_COMPANY,
		"company_exists": company_exists,
		"branches": branch_count,
		"demo_users": user_count
	}


def _operational_data_ready() -> dict:
	results = {"company": {"doctype": "Company", "count": frappe.db.count("Company"), "ready": frappe.db.count("Company") > 0}
	}
	for key, doctype in DEMO_CHECKS:
		if not frappe.db.exists("DocType", doctype):
			results[key] = {"doctype": doctype, "count": 0, "ready": False
	}
			continue
		count = frappe.db.count(doctype)
		results[key] = {"doctype": doctype, "count": count, "ready": count > 0
	}
	return results


def _portal_routes_ready() -> dict:
	missing_pages = []
	for key in PRO_MD_REQUIRED_ROLE_KEYS:
		portal = get_portal_by_key(key)
		if not portal:
			missing_pages.append(key)
			continue
		if not frappe.db.exists("Page", portal["page"]):
			missing_pages.append(key)
	return {
		"required": len(PRO_MD_REQUIRED_ROLE_KEYS),
		"ready": len(PRO_MD_REQUIRED_ROLE_KEYS) - len(missing_pages),
		"missing": missing_pages
	}


@frappe.whitelist()
def run_pharma_final_audit() -> dict:
	evaluation = get_pharma_evaluation_score()
	benchmark = get_global_trading_score()
	gaps = get_gap_status()
	sidebar = _sidebar_clean()
	demo = _demo_company_ready()
	operations = _operational_data_ready()
	portals = _portal_routes_ready()

	ops_ready = sum(1 for v in operations.values() if v.get("ready"))
	ops_total = len(operations)
	all_pass = (
		evaluation.get("evaluation_score", 0) >= 100
		and gaps.get("gaps_open", 1) == 0
		and sidebar.get("clean")
		and not portals.get("missing")
		and demo.get("company_exists")
		and operations.get("pharma_batch", {}).get("ready")
		and operations.get("import_license", {}).get("ready")
		and operations.get("export_shipment", {}).get("ready")
	)

	return {
		"audit_pass": all_pass,
		"evaluation_score": evaluation.get("evaluation_score"),
		"benchmark_score": benchmark.get("weighted_score"),
		"gaps_closed": gaps.get("gaps_closed"),
		"gaps_total": gaps.get("gaps_total"),
		"sidebar": sidebar,
		"demo": demo,
		"operations": operations,
		"operations_ready_pct": round(ops_ready / ops_total * 100, 1) if ops_total else 0,
		"portals": portals,
		"total_portals": len(PHARMA_ROLE_PORTALS),
		"recommendations": _recommendations(sidebar, demo, operations, portals)}


def _recommendations(sidebar, demo, operations, portals) -> list[str]:
	recs = []
	if not sidebar.get("clean"):
		recs.append("Remove legacy 'Pharma Warehouse Management' workspace from sidebar.")
	if not demo.get("company_exists"):
		recs.append("Run pharma demo setup: omnexa_trading.omnexa_trading.data.pharma_demo_setup.run_pharma_demo_setup")
	if portals.get("missing"):
		recs.append(f"Scaffold missing role portals: {', '.join(portals['missing'])}")
	if operations.get("pharma_batch", {}).get("count", 0) == 0:
		recs.append("Seed pharma batches and import/export documents for realistic demo.")
	return recs
