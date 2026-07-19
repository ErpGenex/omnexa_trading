# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPharmaPortalCatalog(FrappeTestCase):
	def test_pharma_portal_catalog_has_all_pro_md_roles(self):
		from omnexa_trading.pharma_portal_catalog import PHARMA_ROLE_PORTALS, PRO_MD_REQUIRED_ROLE_KEYS

		keys = {p["key"] for p in PHARMA_ROLE_PORTALS}
		for required in PRO_MD_REQUIRED_ROLE_KEYS:
			self.assertIn(required, keys, f"Missing pro.md role portal: {required}")
		self.assertGreaterEqual(len(PHARMA_ROLE_PORTALS), 26)

	def test_grouped_pharma_portal_catalog(self):
		from omnexa_trading.pharma_portal_catalog import get_grouped_pharma_portal_catalog

		groups = get_grouped_pharma_portal_catalog(include_missing=1)
		self.assertTrue(len(groups) >= 6)

	def test_role_portal_context(self):
		frappe.set_user("Administrator")
		from omnexa_trading.pharma_portal_catalog import get_role_portal_context

		ctx = get_role_portal_context("quality-manager")
		self.assertEqual(ctx["portal"]["key"], "quality-manager")
		self.assertTrue(len(ctx.get("menu_sections", [])) >= 1)
		self.assertIn("dashboard", ctx)

	def test_trading_portal_catalog_uses_pharma(self):
		frappe.set_user("Administrator")
		from omnexa_trading.trading_portal_catalog import get_grouped_portal_catalog

		groups = get_grouped_portal_catalog(include_missing=1)
		portals = []
		for g in groups:
			portals.extend(g.get("portals") or [])
		self.assertGreaterEqual(len(portals), 26)

	def test_gap_register_includes_pharma_gaps(self):
		from omnexa_trading.trading_gap_register import GAP_DEFINITIONS, GAPS_TOTAL

		self.assertEqual(GAPS_TOTAL, 75)
		pharma_gaps = [g for g in GAP_DEFINITIONS if g.get("domain") == "pharma"]
		self.assertGreaterEqual(len(pharma_gaps), 25)

	def test_new_pharma_doctypes_defined(self):
		for dt in (
			"Pharma Export Shipment",
			"Pharma Import License",
			"Pharma Sample Register",
			"Pharma Drug License",
		):
			self.assertTrue(frappe.db.exists("DocType", dt), f"Missing DocType: {dt}")

	def test_role_portal_dashboard(self):
		frappe.set_user("Administrator")
		from omnexa_trading.pharma_portal_dashboard import get_role_portal_dashboard

		dashboard = get_role_portal_dashboard("ceo")
		self.assertTrue(dashboard.get("kpis"))
		self.assertIn("work_queue", dashboard)
		self.assertIn("quick_actions", dashboard)

	def test_executive_dashboard_has_pos_menu(self):
		from omnexa_trading.pharma_portal_catalog import get_portal_by_key

		portal = get_portal_by_key("executive-dashboard")
		sections = {s["title_en"] for s in portal.get("menu_sections", [])}
		self.assertIn("Point of Sale (POS)", sections)

	def test_executive_dashboard_pos_kpis(self):
		frappe.set_user("Administrator")
		from omnexa_trading.pharma_portal_dashboard import get_role_portal_dashboard

		dashboard = get_role_portal_dashboard("executive-dashboard")
		titles = {k.get("title_en") for k in dashboard.get("kpis", [])}
		self.assertIn("POS Sales Today", titles)
		actions = {a.get("label_en") for a in dashboard.get("quick_actions", [])}
		self.assertIn("Point of Sale", actions)
		pos_action = next(a for a in dashboard.get("quick_actions", []) if a.get("label_en") == "Point of Sale")
		self.assertEqual(pos_action.get("route"), "/app/retail-pos")

	def test_pharma_evaluation_score(self):
		frappe.set_user("Administrator")
		from omnexa_trading.pharma_evaluation import get_pharma_evaluation_score

		result = get_pharma_evaluation_score()
		self.assertEqual(result["target_score"], 100)
		self.assertIn("evaluation_score", result)
		self.assertEqual(result["pro_md_roles_required"], 26)

	def test_trading_pos_retail_phase(self):
		from omnexa_trading.api.trading_deployment_phase_hub import PHASE_DEFINITIONS

		pos = next(p for p in PHASE_DEFINITIONS if p["id"] == "pos_retail")
		self.assertIn("cashier", pos["portal_ids"])
		self.assertIn("customer-service", pos["portal_ids"])

	def test_pharma_child_doctypes_installed(self):
		for dt in (
			"CAPA Team Member",
			"CAPA Action",
			"Assessment Question",
			"Assessment Result",
			"Quality Parameter",
			"Test Result",
		):
			self.assertTrue(frappe.db.exists("DocType", dt), f"Missing DocType: {dt}")

	def test_point_of_sale_page_exists(self):
		self.assertTrue(frappe.db.exists("Page", "point-of-sale"))
		self.assertTrue(frappe.db.exists("Page", "retail-pos"))

	def test_pos_invoice_route_and_page(self):
		from omnexa_trading.trading_pos_routes import (
			get_pos_closing_entry_route,
			get_pos_invoice_list_route,
			get_pos_opening_entry_route,
		)

		self.assertTrue(frappe.db.exists("Page", "pos-invoice"))
		self.assertTrue(frappe.db.exists("Page", "pos-opening-entry"))
		self.assertTrue(frappe.db.exists("Page", "pos-closing-entry"))
		route = get_pos_invoice_list_route()
		if frappe.db.exists("DocType", "POS Invoice"):
			self.assertEqual(route, "/app/List/POS Invoice")
		else:
			self.assertEqual(route, "/app/sales-invoice?is_pos=1")
		if not frappe.db.exists("DocType", "POS Opening Entry"):
			self.assertIn("POS Profile", get_pos_opening_entry_route())
		if not frappe.db.exists("DocType", "POS Closing Entry"):
			self.assertTrue(get_pos_closing_entry_route())
