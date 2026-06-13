# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Export Trading global audit bundle to Docs."""

from __future__ import annotations

import json
import os
from typing import Any

import frappe
from frappe.utils import get_bench_path

from omnexa_trading.trading_gap_register import get_gap_status
from omnexa_trading.trading_global_benchmark import get_global_trading_score


def _audit_root() -> str:
	return os.path.join(get_bench_path(), "Docs", "2026-06-06_OMNEXA_TRADING_GLOBAL_AUDIT")


@frappe.whitelist()
def export_trading_global_audit() -> dict[str, Any]:
	root = _audit_root()
	os.makedirs(root, exist_ok=True)
	score = get_global_trading_score()
	gaps = get_gap_status()
	for name, data in (
		("TRADING_LIVE_SCORE.json", score),
		("TRADING_GAP_REGISTER.json", gaps),
	):
		with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
			json.dump(data, fh, ensure_ascii=False, indent=2)
	return {"path": root, "weighted_score": score.get("weighted_score"), "gaps_open": gaps.get("gaps_open")}
