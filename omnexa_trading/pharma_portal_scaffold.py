# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Scaffold pharmaceutical role portal pages."""

from __future__ import annotations

import json
from pathlib import Path

import frappe

from omnexa_trading.pharma_portal_catalog import MODULE, PHARMA_ROLE_PORTALS

ROLES = [{"role": "System Manager"}, {"role": "Company Admin"}]


def _module_folder() -> Path:
	base = Path(frappe.get_app_path("omnexa_trading"))
	for p in sorted(base.iterdir()):
		if p.is_dir() and (p / "page").is_dir():
			return p
	return base / "omnexa_trading"


def _page_js(page_name: str, role_key: str) -> str:
	return f'''frappe.pages["{page_name}"].on_page_load = function (wrapper) {{
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountPharmaDesk) {{
		omnexa_core.vertical_portal.mountPharmaDesk(wrapper, "{role_key}");
		return;
	}}
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountRoleDesk) {{
		omnexa_core.vertical_portal.mountRoleDesk(wrapper, "omnexa_trading", "{role_key}");
		return;
	}}
	const page = frappe.ui.make_app_page({{
		parent: wrapper,
		title: __("{page_name}"),
		single_column: true,
	}});
	$(page.body).html("<p class=\\"text-muted\\">" + __("Load omnexa_core pharma portal desk") + "</p>");
}};
'''


def scaffold_pharma_portals(*, skip_existing_js: bool = False) -> list[dict]:
	module_root = _module_folder()
	out = []
	for portal in PHARMA_ROLE_PORTALS:
		page_name = portal["page"]
		role_key = portal["key"]
		if page_name in ("trading-workcenter",):
			continue
		folder = page_name.replace("-", "_")
		page_dir = module_root / "page" / folder
		page_dir.mkdir(parents=True, exist_ok=True)
		(page_dir / "__init__.py").write_text("")
		(page_dir / f"{folder}.py").write_text("")

		page_json = {
			"doctype": "Page",
			"module": MODULE,
			"name": page_name,
			"page_name": page_name,
			"standard": "Yes",
			"title": portal["label_en"],
			"roles": ROLES,
		}
		(page_dir / f"{folder}.json").write_text(json.dumps(page_json, indent="\t") + "\n")
		js_path = page_dir / f"{folder}.js"
		if not skip_existing_js or not js_path.exists():
			js_path.write_text(_page_js(page_name, role_key))

		if not frappe.db.exists("Page", page_name):
			from frappe.modules.import_file import import_file_by_path

			import_file_by_path(str(page_dir / f"{folder}.json"), force=True, ignore_version=True)
		else:
			frappe.db.set_value("Page", page_name, "title", portal["label_en"], update_modified=False)

		out.append({"page": page_name, "role": role_key})
	return out


@frappe.whitelist()
def scaffold_all_pharma_portals() -> dict:
	frappe.only_for("System Manager")
	scaffolded = scaffold_pharma_portals()
	frappe.db.commit()
	return {"scaffolded": scaffolded, "count": len(scaffolded)}
