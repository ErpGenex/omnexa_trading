# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Trading role demo credentials for workcenter hub."""

from __future__ import annotations

import frappe

DEMO_PASSWORD = "Pharma@Demo2026"

TRADING_DEMO_SPECS: list[dict] = [
	{
		"role": "Pharma Warehouse Manager",
		"email": "pharma.warehouse.manager@pharmatrade-egypt.com",
		"first_name": "Ahmed",
		"last_name": "Mohamed",
		"route": "/app/trading-warehouse-manager",
	},
	{
		"role": "Pharma Quality Manager",
		"email": "pharma.quality.manager@pharmatrade-egypt.com",
		"first_name": "Sara",
		"last_name": "Ali",
		"route": "/app/trading-quality-manager",
	},
	{
		"role": "Pharma Sales Representative",
		"email": "pharma.sales.rep@pharmatrade-egypt.com",
		"first_name": "Omar",
		"last_name": "Hassan",
		"route": "/app/trading-van-sales-pwa",
	},
	{
		"role": "Pharma Finance Manager",
		"email": "pharma.finance.manager@pharmatrade-egypt.com",
		"first_name": "Nour",
		"last_name": "Said",
		"route": "/app/trading-finance-desk",
	},
	{
		"role": "Sales Manager",
		"email": "pharma.sales.rep@pharmatrade-egypt.com",
		"first_name": "Omar",
		"last_name": "Hassan",
		"route": "/app/trading-executive-dashboard",
	},
	{
		"role": "Company Admin",
		"email": "pharma.finance.manager@pharmatrade-egypt.com",
		"first_name": "Nour",
		"last_name": "Said",
		"route": "/app/trading-executive-dashboard",
	},
]


def _demo_credentials_payload() -> dict:
	users = []
	for spec in TRADING_DEMO_SPECS:
		users.append(
			{
				"role": spec["role"],
				"email": spec["email"],
				"route": spec["route"],
				"name": f"{spec['first_name']} {spec['last_name']}",
			}
		)
	return {"password": DEMO_PASSWORD, "users": users}


@frappe.whitelist()
def get_trading_demo_credentials() -> dict:
	frappe.only_for("System Manager")
	return _demo_credentials_payload()


@frappe.whitelist()
def run_pharma_demo_setup() -> dict:
	frappe.only_for("System Manager")
	from omnexa_trading.omnexa_trading.data.pharma_demo_setup import run_pharma_demo_setup

	result = run_pharma_demo_setup()
	return {
		"ok": True,
		"message": f"Pharma demo ready — {result.get('company', '')} / {result.get('branch', '')}",
		"result": result,
	}
