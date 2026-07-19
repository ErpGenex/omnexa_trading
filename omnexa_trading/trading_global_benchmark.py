# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Global trading benchmark — SAP SD / Van Sales target 4.85."""

from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_trading.trading_gap_register import GLOBAL_LEADER_TARGET, get_gap_status

REFERENCE_LEADERS = {
	"sap_sd": 4.72,
	"oracle_cx_commerce": 4.58,
	"infor_cloudsuite": 4.55,
	"van_sales_leader": 4.65,
}

DOMAIN_MATRIX: list[dict] = [
	{"id": "integration", "label": "Integration / Governance", "weight": 8, "baseline": 3.2, "refs": "SAP SD"},
	{"id": "organization", "label": "Organization & Network", "weight": 9, "baseline": 3.6, "refs": "SAP CRM"},
	{"id": "field_sales", "label": "Field Sales & Distribution", "weight": 12, "baseline": 3.8, "refs": "Van Sales"},
	{"id": "commission", "label": "Commissions & Incentives", "weight": 8, "baseline": 3.4, "refs": "SAP ICM"},
	{"id": "commercial", "label": "Tenders & Credit", "weight": 9, "baseline": 3.5, "refs": "SAP SD"},
	{"id": "finance", "label": "Finance & GL Bridge", "weight": 10, "baseline": 3.7, "refs": "SAP FI"},
	{"id": "reporting", "label": "Reporting & Analytics", "weight": 10, "baseline": 3.5, "refs": "SAP BW"},
	{"id": "analytics", "label": "Advanced Analytics", "weight": 9, "baseline": 3.3, "refs": "SAP IBP"},
	{"id": "digital", "label": "Digital Channels", "weight": 7, "baseline": 3.1, "refs": "Mobile Van"},
	{"id": "bi", "label": "BI & Executive Dashboards", "weight": 6, "baseline": 3.2, "refs": "SAP Analytics"},
	{"id": "operations", "label": "Operations Automation", "weight": 5, "baseline": 3.4, "refs": "SAP SD"},
	{"id": "security", "label": "Security & RBAC", "weight": 4, "baseline": 3.6, "refs": "ISO 27001"},
	{"id": "compliance", "label": "Compliance & Parity", "weight": 3, "baseline": 3.5, "refs": "SAP Parity"},
	{"id": "pharma", "label": "Pharma Role Portals", "weight": 5, "baseline": 3.8, "refs": "pro.md"},
]


def _domain_uplift(closed: int, total: int, baseline: float) -> float:
	if total <= 0:
		return 0.0
	return round((closed / total) * (4.95 - baseline), 2)


def _score_matrix(gap_rows: list[dict]) -> list[dict]:
	by_domain: dict[str, list[dict]] = {}
	for g in gap_rows:
		by_domain.setdefault(g["domain"], []).append(g)
	out = []
	for row in DOMAIN_MATRIX:
		domain_gaps = by_domain.get(row["id"], [])
		total = len(domain_gaps) or 1
		closed = sum(1 for g in domain_gaps if g.get("status") == "closed")
		score = min(4.95, round(row["baseline"] + _domain_uplift(closed, total, row["baseline"]), 2))
		out.append({**row, "score": score, "gaps_closed": closed, "gaps_in_domain": total})
	return out


def _estimate_ranking(weighted: float) -> dict:
	if weighted >= 4.85:
		return {"tier": "Global #1", "label_ar": "المركز الأول عالمياً (بوابة التقييم الداخلي)", "confidence": "high"}
	if weighted >= 4.5:
		return {"tier": "Global Top 10", "label_ar": "أفضل 10 عالمياً", "confidence": "medium"}
	return {"tier": "Developing", "label_ar": "قيد التطوير", "confidence": "medium"}


@frappe.whitelist()
def get_global_trading_score() -> dict:
	gap_status = get_gap_status()
	matrix = _score_matrix(gap_status["gaps"])
	total_weight = sum(r["weight"] for r in matrix)
	weighted = round(sum(r["weight"] * r["score"] for r in matrix) / total_weight, 2) if total_weight else 0
	leader_avg = round(sum(REFERENCE_LEADERS.values()) / len(REFERENCE_LEADERS), 2)

	evaluation = {}
	try:
		from omnexa_trading.pharma_evaluation import get_pharma_evaluation_score

		evaluation = get_pharma_evaluation_score()
	except Exception:
		evaluation = {"evaluation_score": 0, "target_score": 100}

	eval_score = flt(evaluation.get("evaluation_score"))
	return {
		"weighted_score": weighted,
		"evaluation_score": eval_score,
		"evaluation_target": 100,
		"evaluation_grade": evaluation.get("grade"),
		"global_leader_target": GLOBAL_LEADER_TARGET,
		"global_leader_gate": weighted >= GLOBAL_LEADER_TARGET and gap_status["gaps_open"] == 0 and eval_score >= 100,
		"leader_reference_avg": leader_avg,
		"reference_leaders": REFERENCE_LEADERS,
		"parity_pct_vs_leaders": round(weighted / leader_avg * 100, 1) if leader_avg else 0,
		"matrix": matrix,
		"ranking": _estimate_ranking(weighted),
		"pharma_evaluation": evaluation,
		**{k: gap_status[k] for k in ("gaps_closed", "gaps_total", "gaps_open", "version")},
		"app": "omnexa_trading",
		"standards": ["SAP SD Parity", "IFRS 15 Revenue", "ISO 27001", "pro.md Role Portals"],
		"wave": "global-trading-1",
	}
