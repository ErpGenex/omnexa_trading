# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Trading gap register — 48 items vs SAP SD / Van Sales leaders."""

from __future__ import annotations

import os

import frappe
from frappe.utils import get_bench_path

GLOBAL_LEADER_TARGET = 4.85
GAPS_TOTAL = 75
APP = "omnexa_trading"

GAP_DEFINITIONS: list[dict] = [
	{"id": "TD-001", "domain": "integration", "title": "Global trading benchmark module", "wave": 1, "detect": "module:trading_global_benchmark"
	},
	{"id": "TD-002", "domain": "integration", "title": "Trading gap register", "wave": 1, "detect": "module:trading_gap_register"
	},
	{"id": "TD-003", "domain": "integration", "title": "Full workspace sync module", "wave": 1, "detect": "module:workspace.trading_workspace"
	},
	{"id": "TD-004", "domain": "integration", "title": "Trading assessment export module", "wave": 1, "detect": "module:trading_assessment"
	},
	{"id": "TD-005", "domain": "organization", "title": "Omnexa Sales Settings", "wave": 1, "detect": "doctype:Omnexa Sales Settings"
	},
	{"id": "TD-006", "domain": "organization", "title": "Customer Profile master", "wave": 1, "detect": "doctype:Customer Profile"
	},
	{"id": "TD-007", "domain": "organization", "title": "Customer master", "wave": 1, "detect": "doctype:Customer"
	},
	{"id": "TD-008", "domain": "organization", "title": "Distribution Zone", "wave": 1, "detect": "doctype:Distribution Zone"
	},
	{"id": "TD-009", "domain": "organization", "title": "Trading Vehicle", "wave": 1, "detect": "doctype:Trading Vehicle"
	},
	{"id": "TD-010", "domain": "organization", "title": "Trading Sales Representative", "wave": 1, "detect": "doctype:Trading Sales Representative"
	},
	{"id": "TD-011", "domain": "field_sales", "title": "Trading Route Plan", "wave": 1, "detect": "doctype:Trading Route Plan"
	},
	{"id": "TD-012", "domain": "field_sales", "title": "Trading Route Plan Stop", "wave": 1, "detect": "doctype:Trading Route Plan Stop"
	},
	{"id": "TD-013", "domain": "field_sales", "title": "Trading Distribution Order", "wave": 1, "detect": "doctype:Trading Distribution Order"
	},
	{"id": "TD-014", "domain": "field_sales", "title": "Trading Van Sales Invoice", "wave": 1, "detect": "doctype:Trading Van Sales Invoice"
	},
	{"id": "TD-015", "domain": "field_sales", "title": "Trading Vehicle Stock Transfer", "wave": 1, "detect": "doctype:Trading Vehicle Stock Transfer"
	},
	{"id": "TD-016", "domain": "commission", "title": "Trading Commission Rule", "wave": 1, "detect": "doctype:Trading Commission Rule"
	},
	{"id": "TD-017", "domain": "commission", "title": "Trading Commission Settlement", "wave": 1, "detect": "doctype:Trading Commission Settlement"
	},
	{"id": "TD-018", "domain": "commission", "title": "Trading Commission Tier", "wave": 1, "detect": "doctype:Trading Commission Tier"
	},
	{"id": "TD-019", "domain": "commercial", "title": "Trading Tender", "wave": 1, "detect": "doctype:Trading Tender"
	},
	{"id": "TD-020", "domain": "commercial", "title": "Trading Tender Competitor", "wave": 1, "detect": "doctype:Trading Tender Competitor"
	},
	{"id": "TD-021", "domain": "commercial", "title": "Trading Installment Contract", "wave": 1, "detect": "doctype:Trading Installment Contract"
	},
	{"id": "TD-022", "domain": "commercial", "title": "Trading Installment Schedule", "wave": 1, "detect": "doctype:Trading Installment Schedule"
	},
	{"id": "TD-023", "domain": "finance", "title": "GL journal bridge module", "wave": 1, "detect": "module:utils.gl"
	},
	{"id": "TD-024", "domain": "finance", "title": "GL sales sync API", "wave": 1, "detect": "api:omnexa_trading.gl_sales_bridge.sync_van_sales_to_gl"
	},
	{"id": "TD-025", "domain": "finance", "title": "Sales Invoice integration", "wave": 1, "detect": "doctype:Sales Invoice"
	},
	{"id": "TD-026", "domain": "finance", "title": "Payment Entry integration", "wave": 1, "detect": "doctype:Payment Entry"
	},
	{"id": "TD-027", "domain": "reporting", "title": "Trading Sales Summary report", "wave": 1, "detect": "report:Trading Sales Summary"
	},
	{"id": "TD-028", "domain": "reporting", "title": "Distribution Fulfillment report", "wave": 1, "detect": "report:Trading Distribution Fulfillment"
	},
	{"id": "TD-029", "domain": "reporting", "title": "Vehicle Transfer Summary report", "wave": 1, "detect": "report:Trading Vehicle Transfer Summary"
	},
	{"id": "TD-030", "domain": "reporting", "title": "Route Efficiency report", "wave": 1, "detect": "report:Trading Route Efficiency"
	},
	{"id": "TD-031", "domain": "reporting", "title": "Rep Target Tracking report", "wave": 1, "detect": "report:Trading Rep Target Tracking"
	},
	{"id": "TD-032", "domain": "reporting", "title": "Commission Summary report", "wave": 1, "detect": "report:Trading Commission Summary"
	},
	{"id": "TD-033", "domain": "reporting", "title": "Tender Pipeline report", "wave": 1, "detect": "report:Trading Tender Pipeline"
	},
	{"id": "TD-034", "domain": "reporting", "title": "Installment Portfolio report", "wave": 1, "detect": "report:Trading Installment Portfolio"
	},
	{"id": "TD-035", "domain": "reporting", "title": "POS Z Report Reconciliation", "wave": 1, "detect": "report:POS Z Report Reconciliation"
	},
	{"id": "TD-036", "domain": "analytics", "title": "Distribution dashboard API", "wave": 2, "detect": "api:omnexa_trading.distribution_api.get_distribution_dashboard"
	},
	{"id": "TD-037", "domain": "analytics", "title": "Route optimization API", "wave": 2, "detect": "api:omnexa_trading.trading_global_extensions.optimize_route_stops"
	},
	{"id": "TD-038", "domain": "analytics", "title": "Commission forecast API", "wave": 2, "detect": "api:omnexa_trading.trading_global_extensions.compute_commission_forecast"
	},
	{"id": "TD-039", "domain": "analytics", "title": "Customer credit limit API", "wave": 2, "detect": "api:omnexa_trading.trading_global_extensions.check_customer_credit_limit"
	},
	{"id": "TD-040", "domain": "analytics", "title": "Van stock IoT levels API", "wave": 2, "detect": "api:omnexa_trading.trading_global_extensions.get_van_stock_iot_levels"
	},
	{"id": "TD-041", "domain": "analytics", "title": "Tender win probability API", "wave": 2, "detect": "api:omnexa_trading.trading_global_extensions.analyze_tender_win_probability"
	},
	{"id": "TD-042", "domain": "digital", "title": "Executive dashboard page", "wave": 2, "detect": "page:trading-executive-dashboard"
	},
	{"id": "TD-043", "domain": "digital", "title": "Van sales PWA page", "wave": 2, "detect": "page:trading-van-sales-pwa"
	},
	{"id": "TD-044", "domain": "bi", "title": "Sector KPI preview bridge", "wave": 1, "detect": "api:omnexa_trading.trading_portal_catalog.preview_sector_kpi"
	},
	{"id": "TD-045", "domain": "operations", "title": "Installment penalty scheduler", "wave": 1, "detect": "module:tasks"
	},
	{"id": "TD-046", "domain": "security", "title": "Branch-scoped RBAC permissions", "wave": 1, "detect": "file:permissions.py"
	},
	{"id": "TD-047", "domain": "compliance", "title": "SAP parity regression test", "wave": 1, "detect": "file:tests/test_sap_parity_sector.py"
	},
	{"id": "TD-048", "domain": "finance", "title": "Cost Center integration", "wave": 1, "detect": "doctype:Cost Center"
	},
	{"id": "TD-049", "domain": "pharma", "title": "Pharma portal catalog SSOT", "wave": 1, "detect": "module:pharma_portal_catalog"
	},
	{"id": "TD-050", "domain": "pharma", "title": "Pharma portal scaffold", "wave": 1, "detect": "module:pharma_portal_scaffold"
	},
	{"id": "TD-051", "domain": "pharma", "title": "Pharma Export Shipment DocType", "wave": 1, "detect": "doctype:Pharma Export Shipment"
	},
	{"id": "TD-052", "domain": "pharma", "title": "Pharma Import License DocType", "wave": 1, "detect": "doctype:Pharma Import License"
	},
	{"id": "TD-053", "domain": "pharma", "title": "Pharma Sample Register DocType", "wave": 1, "detect": "doctype:Pharma Sample Register"
	},
	{"id": "TD-054", "domain": "pharma", "title": "Pharma Drug License DocType", "wave": 1, "detect": "doctype:Pharma Drug License"
	},
	{"id": "TD-055", "domain": "pharma", "title": "Quality Manager portal page", "wave": 2, "detect": "page:trading-quality-manager"
	},
	{"id": "TD-056", "domain": "pharma", "title": "Import Manager portal page", "wave": 2, "detect": "page:trading-import-manager"
	},
	{"id": "TD-057", "domain": "pharma", "title": "Export Manager portal page", "wave": 2, "detect": "page:trading-export-manager"
	},
	{"id": "TD-058", "domain": "pharma", "title": "Cold Chain Manager portal page", "wave": 2, "detect": "page:trading-cold-chain-manager"
	},
	{"id": "TD-059", "domain": "pharma", "title": "Regulatory Officer portal page", "wave": 2, "detect": "page:trading-regulatory-officer"
	},
	{"id": "TD-060", "domain": "pharma", "title": "Pharma gap closure patch", "wave": 1, "detect": "file:patches/v1_0/close_pharma_gaps.py"
	},
	{"id": "TD-061", "domain": "pharma", "title": "Pharma evaluation score module", "wave": 2, "detect": "module:pharma_evaluation"
	},
	{"id": "TD-062", "domain": "pharma", "title": "Role portal dashboard API", "wave": 2, "detect": "api:omnexa_trading.pharma_portal_dashboard.get_role_portal_dashboard"
	},
	{"id": "TD-063", "domain": "pharma", "title": "CEO portal page", "wave": 2, "detect": "page:trading-ceo"
	},
	{"id": "TD-064", "domain": "pharma", "title": "Chairman portal page", "wave": 2, "detect": "page:trading-chairman"
	},
	{"id": "TD-065", "domain": "pharma", "title": "Finance Director portal page", "wave": 2, "detect": "page:trading-finance-director"
	},
	{"id": "TD-066", "domain": "pharma", "title": "HR Director portal page", "wave": 2, "detect": "page:trading-hr-director"
	},
	{"id": "TD-067", "domain": "pharma", "title": "Area Manager portal page", "wave": 2, "detect": "page:trading-area-manager"
	},
	{"id": "TD-068", "domain": "pharma", "title": "Sales Supervisor portal page", "wave": 2, "detect": "page:trading-sales-supervisor"
	},
	{"id": "TD-069", "domain": "pharma", "title": "Customer Service portal page", "wave": 2, "detect": "page:trading-customer-service"
	},
	{"id": "TD-070", "domain": "pharma", "title": "Treasury portal page", "wave": 2, "detect": "page:trading-treasury"
	},
	{"id": "TD-071", "domain": "pharma", "title": "Cashier portal page", "wave": 2, "detect": "page:trading-cashier"
	},
	{"id": "TD-072", "domain": "pharma", "title": "Store Keeper portal page", "wave": 2, "detect": "page:trading-store-keeper"
	},
	{"id": "TD-073", "domain": "pharma", "title": "Dispatch portal page", "wave": 2, "detect": "page:trading-dispatch"
	},
	{"id": "TD-074", "domain": "pharma", "title": "Receiving portal page", "wave": 2, "detect": "page:trading-receiving"
	},
	{"id": "TD-075", "domain": "pharma", "title": "Operations Director portal page", "wave": 2, "detect": "page:trading-operations-director"
	},
]

def _detect_gap(gap: dict) -> bool:
	detect = gap.get("detect")
	if not detect:
		return False
	try:
		if detect.startswith("doctype:"):
			return bool(frappe.db.exists("DocType", detect.split(":", 1)[1]))
		if detect.startswith("page:"):
			return bool(frappe.db.exists("Page", detect.split(":", 1)[1]))
		if detect.startswith("report:"):
			return bool(frappe.db.exists("Report", detect.split(":", 1)[1]))
		if detect.startswith("api:"):
			return bool(frappe.get_attr(detect.split(":", 1)[1]))
		if detect.startswith("module:"):
			return bool(frappe.get_module(f"{APP}.{detect.split(':', 1)[1]}"))
		if detect.startswith("file:"):
			rel = detect.split(":", 1)[1]
			root = os.path.join(get_bench_path(), "apps", APP, APP)
			return os.path.isfile(os.path.join(root, rel))
	except Exception:
		return False
	return False


def get_gap_status() -> dict:
	rows = []
	closed = 0
	for gap in GAP_DEFINITIONS:
		is_closed = _detect_gap(gap)
		if is_closed:
			closed += 1
		rows.append({**gap, "status": "closed" if is_closed else "open"
	})
	return {
		"version": "2026.06.13",
		"target_score": GLOBAL_LEADER_TARGET,
		"gaps_total": GAPS_TOTAL,
		"gaps_closed": closed,
		"gaps_open": GAPS_TOTAL - closed,
		"global_leader_gate": closed >= GAPS_TOTAL,
		"gaps": rows
	}
