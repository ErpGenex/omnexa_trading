# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_trading.trading_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from omnexa_trading.trading_global_benchmark import get_global_trading_score
from omnexa_trading.workspace.trading_workspace import sync_trading_workspace_menu


class TestTradingGlobalBenchmark(FrappeTestCase):
	def test_global_score_returns_matrix(self):
		score = get_global_trading_score()
		self.assertIn("weighted_score", score)
		self.assertGreaterEqual(score["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(score.get("global_leader_gate"))
		self.assertEqual(score["gaps_total"], 48)
		self.assertEqual(score["gaps_open"], 0)

	def test_gap_register_all_closed(self):
		gaps = get_gap_status()
		self.assertEqual(gaps["gaps_open"], 0)
		self.assertTrue(gaps["global_leader_gate"])

	def test_workspace_sync(self):
		stats = sync_trading_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["sections"], 5)
		self.assertGreater(stats["total_links"], 25)
		self.assertGreater(stats["shortcuts"], stats["total_links"] - 1)
		self.assertGreater(stats["content_blocks"], stats["total_links"])

		ws = frappe.get_doc("Workspace", "Trading")
		shortcut_labels = {s.label for s in ws.shortcuts}
		for block in json.loads(ws.content or "[]"):
			if block.get("type") != "shortcut":
				continue
			self.assertIn(block["data"]["shortcut_name"], shortcut_labels)
