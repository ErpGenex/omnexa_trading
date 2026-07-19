# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Ensure pharma compliance child DocTypes stay synced after migrate."""

from __future__ import annotations

import frappe

CHILD_DOCTYPES = (
	("capa_team_member", "CAPA Team Member"),
	("capa_action", "CAPA Action"),
	("assessment_question", "Assessment Question"),
	("assessment_result", "Assessment Result"),
	("quality_parameter", "Quality Parameter"),
	("batch_serial_number", "Batch Serial Number"),
	("test_result", "Test Result"),
	("inspection_defect", "Inspection Defect"),
	("field_change", "Field Change"),
	("inspection_photo", "Inspection Photo"),
)


def execute() -> None:
	for folder, name in CHILD_DOCTYPES:
		frappe.reload_doc("Omnexa Trading", "doctype", folder)
		if not frappe.db.exists("DocType", name):
			frappe.reload_doc("Omnexa Trading", "doctype", folder, force=True)
	frappe.db.commit()
