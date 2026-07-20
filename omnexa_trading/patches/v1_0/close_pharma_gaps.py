# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Close pharmaceutical trading gaps — portals, workspace, roles, doctypes."""

from __future__ import annotations


def execute():
	import frappe

	from omnexa_trading.pharma_portal_scaffold import scaffold_pharma_portals
	from omnexa_trading.workspace.trading_workspace import sync_trading_workspace_menu

	# Scaffold all pharma role portal pages
	scaffolded = scaffold_pharma_portals(skip_existing_js=True)

	# Sync full trading workspace with pharma sections
	sync_trading_workspace_menu(save=True, rebuild=True)

	# Ensure pharma roles exist
	from omnexa_trading.omnexa_trading.data.pharma_demo_setup import create_pharma_roles

	create_pharma_roles()

	frappe.db.commit()
	return {"scaffolded": len(scaffolded), "status": "pharma_gaps_closed"
	}
