# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe

from omnexa_core.omnexa_core.branch_access import enforce_branch_access, get_allowed_branches
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
	enforce_branch_access(doc)


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def _get_query_for_table(table: str, user=None):
	user = user or frappe.session.user
	allowed = get_allowed_branches(user)
	if allowed is None:
		return ""
	if not allowed:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(v) for v in allowed])
	return f"(`tab{table}`.branch in ({quoted}) or `tab{table}`.branch is null or `tab{table}`.branch = '')"


def trading_sales_representative_query_conditions(user=None):
	return _get_query_for_table("Trading Sales Representative", user)


def trading_vehicle_query_conditions(user=None):
	return _get_query_for_table("Trading Vehicle", user)


def distribution_zone_query_conditions(user=None):
	return _get_query_for_table("Distribution Zone", user)


def trading_route_plan_query_conditions(user=None):
	return _get_query_for_table("Trading Route Plan", user)


def trading_commission_rule_query_conditions(user=None):
	return _get_query_for_table("Trading Commission Rule", user)


def trading_distribution_order_query_conditions(user=None):
	return _get_query_for_table("Trading Distribution Order", user)


def trading_vehicle_stock_transfer_query_conditions(user=None):
	return _get_query_for_table("Trading Vehicle Stock Transfer", user)


def trading_van_sales_invoice_query_conditions(user=None):
	return _get_query_for_table("Trading Van Sales Invoice", user)


def trading_commission_settlement_query_conditions(user=None):
	return _get_query_for_table("Trading Commission Settlement", user)


def trading_tender_query_conditions(user=None):
	return _get_query_for_table("Trading Tender", user)


def trading_installment_contract_query_conditions(user=None):
	return _get_query_for_table("Trading Installment Contract", user)

