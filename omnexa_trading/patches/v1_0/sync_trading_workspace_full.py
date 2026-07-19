# Copyright (c) 2026, Omnexa

import frappe


def execute() -> None:
	if not frappe.db.exists("Workspace", "Trading"):
		return
	from omnexa_trading.workspace.trading_workspace import sync_trading_workspace_menu

	sync_trading_workspace_menu(save=True, rebuild=True)
