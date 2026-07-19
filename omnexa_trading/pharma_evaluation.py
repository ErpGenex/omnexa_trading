# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Pharmaceutical trading evaluation score — target 100/100."""

from __future__ import annotations

import frappe

from omnexa_trading.pharma_portal_catalog import PHARMA_ROLE_PORTALS, PRO_MD_REQUIRED_ROLE_KEYS, get_portal_by_key
from omnexa_trading.trading_gap_register import get_gap_status

PORTAL_COMPONENTS = (
	"role_dashboard",
	"work_queue",
	"pending_tasks",
	"approvals",
	"kpis",
	"charts",
	"quick_actions",
	"reports",
	"notifications",
)


def _role_portal_coverage() -> dict:
	by_key = {p["key"]: p for p in PHARMA_ROLE_PORTALS}
	missing_keys = [k for k in PRO_MD_REQUIRED_ROLE_KEYS if k not in by_key]
	pages_ok = []
	pages_missing = []
	incomplete = []

	for key in PRO_MD_REQUIRED_ROLE_KEYS:
		portal = by_key.get(key)
		if not portal:
			continue
		page = portal.get("page")
		if page and frappe.db.exists("Page", page):
			pages_ok.append(key)
		else:
			pages_missing.append(key)
		if not portal.get("menu_sections") or not portal.get("commerce_role") or not portal.get("route"):
			incomplete.append(key)

	total = len(PRO_MD_REQUIRED_ROLE_KEYS)
	return {
		"required_roles": total,
		"defined_roles": total - len(missing_keys),
		"pages_ready": len(pages_ok),
		"missing_keys": missing_keys,
		"pages_missing": pages_missing,
		"incomplete_portals": incomplete,
		"coverage_pct": round(len(pages_ok) / total * 100, 1) if total else 0,
	}


def _portal_component_coverage() -> dict:
	from omnexa_trading.pharma_portal_dashboard import get_role_portal_dashboard

	ready = 0
	details = []
	for key in PRO_MD_REQUIRED_ROLE_KEYS:
		portal = get_portal_by_key(key)
		if not portal:
			details.append({"key": key, "ready": False, "reason": "missing_portal"})
			continue
		try:
			dashboard = get_role_portal_dashboard(key)
		except Exception as exc:
			details.append({"key": key, "ready": False, "reason": str(exc)})
			continue

		has_all = all(
			dashboard.get("kpis")
			and dashboard.get("work_queue") is not None
			and dashboard.get("pending_tasks") is not None
			and dashboard.get("approvals") is not None
			and dashboard.get("quick_actions")
			and dashboard.get("charts")
			and dashboard.get("notifications")
			and portal.get("menu_sections")
		)
		if has_all:
			ready += 1
		details.append({"key": key, "ready": has_all, "components": list(PORTAL_COMPONENTS)})

	total = len(PRO_MD_REQUIRED_ROLE_KEYS)
	return {
		"roles_with_full_dashboard": ready,
		"component_coverage_pct": round(ready / total * 100, 1) if total else 0,
		"details": details,
	}


@frappe.whitelist()
def get_pharma_evaluation_score() -> dict:
	gap_status = get_gap_status()
	role_cov = _role_portal_coverage()
	component_cov = _portal_component_coverage()

	gap_pct = round(gap_status["gaps_closed"] / gap_status["gaps_total"] * 100, 1) if gap_status["gaps_total"] else 0
	role_pct = role_cov["coverage_pct"]
	component_pct = component_cov["component_coverage_pct"]

	overall = round((gap_pct * 0.35) + (role_pct * 0.35) + (component_pct * 0.30), 1)
	all_roles_ready = (
		not role_cov["missing_keys"]
		and not role_cov["pages_missing"]
		and not role_cov["incomplete_portals"]
		and role_cov["coverage_pct"] >= 100
	)
	all_gaps_closed = gap_status["gaps_open"] == 0
	full_dashboards = component_cov["roles_with_full_dashboard"] == len(PRO_MD_REQUIRED_ROLE_KEYS)

	if all_roles_ready and all_gaps_closed and full_dashboards:
		overall = 100.0

	return {
		"evaluation_score": overall,
		"target_score": 100,
		"grade": "A+" if overall >= 100 else ("A" if overall >= 90 else ("B" if overall >= 80 else "C")),
		"global_leader_gate": overall >= 100,
		"breakdown": {
			"gap_closure_pct": gap_pct,
			"role_portal_coverage_pct": role_pct,
			"portal_component_coverage_pct": component_pct,
		},
		"role_coverage": role_cov,
		"component_coverage": component_cov,
		"gaps_closed": gap_status["gaps_closed"],
		"gaps_total": gap_status["gaps_total"],
		"gaps_open": gap_status["gaps_open"],
		"pro_md_roles_required": len(PRO_MD_REQUIRED_ROLE_KEYS),
		"pro_md_roles_ready": role_cov["pages_ready"],
		"standards": ["pro.md Role Portals", "GDP/GMP", "SAP SD Parity"],
	}
