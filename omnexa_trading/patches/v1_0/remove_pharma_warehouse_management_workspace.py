# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Remove legacy Pharma Warehouse Management workspace from desk sidebar."""

from __future__ import annotations

import frappe

LEGACY_WORKSPACE_NAMES = (
	"إدارة المستودعات - Warehouse Management",
	"Pharma Warehouse Management",
	"pharma-warehouse-management",
)


def execute() -> None:
	removed = []
	for name in LEGACY_WORKSPACE_NAMES:
		if frappe.db.exists("Workspace", name):
			frappe.delete_doc("Workspace", name, force=True, ignore_permissions=True)
			removed.append(name)

	# Also remove any public workspace whose title matches legacy label
	for row in frappe.get_all(
		"Workspace",
		filters={"title": "Pharma Warehouse Management", "module": "Omnexa Trading"
	},
		pluck="name",
	):
		if row not in removed and frappe.db.exists("Workspace", row):
			frappe.delete_doc("Workspace", row, force=True, ignore_permissions=True)
			removed.append(row)

	frappe.db.commit()
	frappe.clear_cache(doctype="Workspace")
	if removed:
		print(f"Removed legacy pharma warehouse workspaces: {', '.join(removed)}")
