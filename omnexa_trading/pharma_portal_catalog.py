# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""Pharmaceutical trading role portal catalog — SSOT for GDP/GMP enterprise operations."""

from __future__ import annotations

import frappe

MODULE = "Omnexa Trading"


def _dt_route(doctype: str) -> str:
	return f"/app/List/{doctype}"


def _pos_invoice_route() -> str:
	from omnexa_trading.trading_pos_routes import get_pos_invoice_list_route

	return get_pos_invoice_list_route()


def _pos_opening_entry_route() -> str:
	from omnexa_trading.trading_pos_routes import get_pos_opening_entry_route

	return get_pos_opening_entry_route()


def _pos_closing_entry_route() -> str:
	from omnexa_trading.trading_pos_routes import get_pos_closing_entry_route

	return get_pos_closing_entry_route()


def _report_route(report: str) -> str:
	return f"/app/query-report/{report}"


def _menu_item(label_en: str, label_ar: str, route: str, icon: str = "📄") -> dict:
	return {"label_en": label_en, "label_ar": label_ar, "route": route, "icon": icon}


def _section(title_en: str, title_ar: str, items: list[dict]) -> dict:
	return {"title_en": title_en, "title_ar": title_ar, "items": items}


# Shared menu blocks
_COMPLIANCE_MENU = _section(
	"Compliance & Quality (GDP/GMP)",
	"الامتثال والجودة",
	[
		_menu_item("CAPA", "الإجراءات التصحيحية", _dt_route("CAPA"), "🔧"),
		_menu_item("Deviations", "الانحرافات", _dt_route("Deviation"), "⚠️"),
		_menu_item("SOP Management", "إجراءات التشغيل", _dt_route("SOP Management"), "📋"),
		_menu_item("Training Records", "سجلات التدريب", _dt_route("Training Record"), "🎓"),
		_menu_item("Electronic Signatures", "التوقيعات الإلكترونية", _dt_route("Electronic Signature"), "✍️"),
		_menu_item("Validation Protocols", "بروتوكولات التحقق", _dt_route("Validation Protocol"), "✅"),
		_menu_item("Risk Assessment", "تقييم المخاطر", _dt_route("Risk Assessment"), "📊"),
		_menu_item("Vendor Qualification", "تأهيل الموردين", _dt_route("Vendor Qualification"), "🏭"),
	],
)

_PHARMA_OPS_MENU = _section(
	"Pharmaceutical Operations",
	"العمليات الدوائية",
	[
		_menu_item("Pharma Batch", "دفعات الأدوية", _dt_route("Pharma Batch"), "💊"),
		_menu_item("Drug Registration", "تسجيل الأدوية", _dt_route("Pharma Drug Registration"), "📝"),
		_menu_item("Quality Inspection", "فحص الجودة", _dt_route("Pharma Quality Inspection"), "🔬"),
		_menu_item("Product Recall", "استدعاء المنتجات", _dt_route("Pharma Product Recall"), "🔄"),
		_menu_item("Regulatory Approval", "الموافقات التنظيمية", _dt_route("Pharma Regulatory Approval"), "🏛️"),
		_menu_item("Drug License", "التراخيص الدوائية", _dt_route("Pharma Drug License"), "📜"),
		_menu_item("Sample Register", "سجل العينات", _dt_route("Pharma Sample Register"), "🧪"),
	],
)

_IMPORT_EXPORT_MENU = _section(
	"Import & Export",
	"الاستيراد والتصدير",
	[
		_menu_item("Import LC", "خطابات الاعتماد", _dt_route("Pharma Import LC"), "🏦"),
		_menu_item("LC Requests", "طلبات الاعتماد", _dt_route("Pharma LC Request"), "📨"),
		_menu_item("Import License", "تراخيص الاستيراد", _dt_route("Pharma Import License"), "📥"),
		_menu_item("Export Shipment", "شحنات التصدير", _dt_route("Pharma Export Shipment"), "📤"),
		_menu_item("Purchase Order", "أوامر الشراء", _dt_route("Purchase Order"), "🛒"),
		_menu_item("Purchase Receipt", "استلام البضائع", _dt_route("Purchase Receipt"), "📦"),
	],
)

_COLD_CHAIN_MENU = _section(
	"Cold Chain (GDP)",
	"السلسلة الباردة",
	[
		_menu_item("Temperature Log", "سجل الحرارة", _dt_route("Temperature Log"), "🌡️"),
		_menu_item("Temperature Excursion", "انحرافات الحرارة", _dt_route("Temperature Excursion"), "❄️"),
		_menu_item("Pharma Batch (Cold)", "دفعات باردة", _dt_route("Pharma Batch"), "💊"),
		_menu_item("Equipment Qualification", "تأهيل المعدات", _dt_route("Equipment Qualification"), "⚙️"),
	],
)

_WAREHOUSE_MENU = _section(
	"Warehouse & Inventory",
	"المخازن والمخزون",
	[
		_menu_item("Stock Entry", "حركة مخزون", _dt_route("Stock Entry"), "📦"),
		_menu_item("Delivery Note", "إذن تسليم", _dt_route("Delivery Note"), "🚚"),
		_menu_item("Purchase Receipt", "استلام", _dt_route("Purchase Receipt"), "📥"),
		_menu_item("Pharma Batch", "دفعات", _dt_route("Pharma Batch"), "💊"),
		_menu_item("Item", "الأصناف", _dt_route("Item"), "🏷️"),
	],
)

_SALES_MENU = _section(
	"Sales & Distribution",
	"المبيعات والتوزيع",
	[
		_menu_item("Sales Order", "أوامر المبيعات", _dt_route("Sales Order"), "🛍️"),
		_menu_item("Sales Invoice", "فواتير المبيعات", _dt_route("Sales Invoice"), "🧾"),
		_menu_item("Distribution Order", "أوامر التوزيع", _dt_route("Trading Distribution Order"), "📋"),
		_menu_item("Van Sales Invoice", "فواتير المندوب", _dt_route("Trading Van Sales Invoice"), "🚐"),
		_menu_item("Route Plan", "خطط المسارات", _dt_route("Trading Route Plan"), "🗺️"),
		_menu_item("Customer", "العملاء", _dt_route("Customer"), "👥"),
	],
)

_FINANCE_MENU = _section(
	"Finance & Treasury",
	"المالية والخزينة",
	[
		_menu_item("Sales Invoice", "فواتير المبيعات", _dt_route("Sales Invoice"), "🧾"),
		_menu_item("Payment Entry", "سندات القبض/الصرف", _dt_route("Payment Entry"), "💳"),
		_menu_item("Journal Entry", "قيود اليومية", _dt_route("Journal Entry"), "📒"),
		_menu_item("GL Account", "دليل الحسابات", _dt_route("GL Account"), "📊"),
		_menu_item("Sales Summary", "ملخص المبيعات", _report_route("Trading Sales Summary"), "📈"),
	],
)

_HR_MENU = _section(
	"Human Resources",
	"الموارد البشرية",
	[
		_menu_item("Employee", "الموظفون", _dt_route("Employee"), "👥"),
		_menu_item("Training Records", "سجلات التدريب", _dt_route("Training Record"), "🎓"),
		_menu_item("Sales Representative", "المندوبين", _dt_route("Trading Sales Representative"), "🚐"),
		_menu_item("Commission Settlement", "تسوية العمولات", _dt_route("Trading Commission Settlement"), "💰"),
	],
)

_EXECUTIVE_MENU = _section(
	"Executive Overview",
	"نظرة تنفيذية",
	[
		_menu_item("Executive Dashboard", "لوحة الإدارة", "/app/trading-executive-dashboard", "📊"),
		_menu_item("Sales Summary", "ملخص المبيعات", _report_route("Trading Sales Summary"), "📈"),
		_menu_item("Tender Pipeline", "خط المناقصات", _report_route("Trading Tender Pipeline"), "📋"),
		_menu_item("CAPA", "الإجراءات التصحيحية", _dt_route("CAPA"), "🔧"),
	],
)

_POS_MENU = _section(
	"Point of Sale (POS)",
	"نقاط البيع",
	[
		_menu_item("Point of Sale", "نقطة البيع", "/app/retail-pos", "🛒"),
		_menu_item("POS Invoice", "فواتير نقاط البيع", _pos_invoice_route(), "🧾"),
		_menu_item("POS Profile", "ملفات نقاط البيع", _dt_route("POS Profile"), "⚙️"),
		_menu_item("POS Opening Entry", "فتح الصندوق", _pos_opening_entry_route(), "🔓"),
		_menu_item("POS Closing Entry", "إغلاق الصندوق", _pos_closing_entry_route(), "🔒"),
		_menu_item("Cashier Portal", "بوابة أمين الصندوق", "/app/trading-cashier", "💵"),
		_menu_item("POS Z Reconciliation", "تسوية نقاط البيع", _report_route("POS Z Report Reconciliation"), "📊"),
	],
)

_DISPATCH_MENU = _section(
	"Dispatch Operations",
	"عمليات التسليم",
	[
		_menu_item("Delivery Note", "إذن تسليم", _dt_route("Delivery Note"), "🚚"),
		_menu_item("Distribution Order", "أوامر التوزيع", _dt_route("Trading Distribution Order"), "📋"),
		_menu_item("Vehicle Stock Transfer", "تحويل مخزون", _dt_route("Trading Vehicle Stock Transfer"), "🚐"),
		_menu_item("Pharma Batch", "دفعات", _dt_route("Pharma Batch"), "💊"),
	],
)

_RECEIVING_MENU = _section(
	"Receiving & QC",
	"الاستلام والفحص",
	[
		_menu_item("Purchase Receipt", "استلام البضائع", _dt_route("Purchase Receipt"), "📥"),
		_menu_item("Purchase Order", "أوامر الشراء", _dt_route("Purchase Order"), "🛒"),
		_menu_item("Quality Inspection", "فحص الجودة", _dt_route("Pharma Quality Inspection"), "🔬"),
		_menu_item("Import License", "تراخيص الاستيراد", _dt_route("Pharma Import License"), "📜"),
	],
)

# pro.md — every role must have an independent portal (26 roles)
PRO_MD_REQUIRED_ROLE_KEYS: tuple[str, ...] = (
	"ceo",
	"chairman",
	"general-manager",
	"commercial-director",
	"operations-director",
	"finance-director",
	"hr-director",
	"warehouse-manager",
	"purchase-manager",
	"import-manager",
	"export-manager",
	"quality-manager",
	"sales-director",
	"medical-rep",
	"area-manager",
	"sales-supervisor",
	"customer-service",
	"treasury",
	"chief-accountant",
	"cashier",
	"inventory-controller",
	"store-keeper",
	"dispatch",
	"receiving",
	"auditor",
	"workcenter",
)

PHARMA_ROLE_PORTALS: list[dict] = [
	{
		"key": "ceo",
		"page": "trading-ceo",
		"route": "/app/trading-ceo",
		"icon": "👑",
		"category": "management",
		"roles": ["Company Admin", "System Manager"],
		"commerce_role": "commerce_general_manager",
		"label_en": "CEO Portal",
		"label_ar": "بوابة الرئيس التنفيذي",
		"role_en": "CEO",
		"role_ar": "الرئيس التنفيذي",
		"menu_sections": [_EXECUTIVE_MENU, _POS_MENU, _PHARMA_OPS_MENU, _SALES_MENU, _FINANCE_MENU, _COMPLIANCE_MENU],
	},
	{
		"key": "chairman",
		"page": "trading-chairman",
		"route": "/app/trading-chairman",
		"icon": "🏛️",
		"category": "management",
		"roles": ["Company Admin"],
		"commerce_role": "commerce_general_manager",
		"label_en": "Chairman Portal",
		"label_ar": "بوابة رئيس مجلس الإدارة",
		"role_en": "Chairman",
		"role_ar": "رئيس مجلس الإدارة",
		"menu_sections": [_EXECUTIVE_MENU, _FINANCE_MENU, _COMPLIANCE_MENU],
	},
	{
		"key": "general-manager",
		"page": "trading-general-manager",
		"route": "/app/trading-general-manager",
		"icon": "👔",
		"category": "management",
		"roles": ["System Manager", "Company Admin"],
		"commerce_role": "commerce_general_manager",
		"label_en": "General Manager Portal",
		"label_ar": "بوابة المدير العام",
		"role_en": "General Manager",
		"role_ar": "المدير العام",
		"menu_sections": [_PHARMA_OPS_MENU, _IMPORT_EXPORT_MENU, _COMPLIANCE_MENU, _SALES_MENU, _FINANCE_MENU],
	},
	{
		"key": "commercial-director",
		"page": "trading-commercial-director",
		"route": "/app/trading-commercial-director",
		"icon": "📊",
		"category": "management",
		"roles": ["Sales Manager", "Company Admin"],
		"commerce_role": "commerce_sales",
		"label_en": "Commercial Director Portal",
		"label_ar": "بوابة المدير التجاري",
		"role_en": "Commercial Director",
		"role_ar": "المدير التجاري",
		"menu_sections": [_SALES_MENU, _section("Tenders & Credit", "المناقصات والائتمان", [
			_menu_item("Tender", "المناقصات", _dt_route("Trading Tender"), "📋"),
			_menu_item("Installment Contract", "عقود التقسيط", _dt_route("Trading Installment Contract"), "💰"),
			_menu_item("Tender Pipeline", "خط المناقصات", _report_route("Trading Tender Pipeline"), "📈"),
		])],
	},
	{
		"key": "warehouse-manager",
		"page": "trading-warehouse-manager",
		"route": "/app/trading-warehouse-manager",
		"icon": "🏭",
		"category": "operations",
		"roles": ["Pharma Warehouse Manager", "Stock Manager", "Stock User"],
		"commerce_role": "commerce_warehouse",
		"label_en": "Warehouse Manager Portal",
		"label_ar": "بوابة مدير المستودع",
		"role_en": "Warehouse Manager",
		"role_ar": "مدير المستودع",
		"menu_sections": [_WAREHOUSE_MENU, _PHARMA_OPS_MENU, _COLD_CHAIN_MENU],
	},
	{
		"key": "purchase-manager",
		"page": "trading-purchase-manager",
		"route": "/app/trading-purchase-manager",
		"icon": "🛒",
		"category": "operations",
		"roles": ["Purchase Manager", "Purchase User"],
		"commerce_role": "commerce_purchasing",
		"label_en": "Purchase Manager Portal",
		"label_ar": "بوابة مدير المشتريات",
		"role_en": "Purchase Manager",
		"role_ar": "مدير المشتريات",
		"menu_sections": [_IMPORT_EXPORT_MENU, _section("Procurement", "المشتريات", [
			_menu_item("Supplier", "الموردون", _dt_route("Supplier"), "🏭"),
			_menu_item("Vendor Qualification", "تأهيل الموردين", _dt_route("Vendor Qualification"), "✅"),
		])],
	},
	{
		"key": "import-manager",
		"page": "trading-import-manager",
		"route": "/app/trading-import-manager",
		"icon": "📥",
		"category": "operations",
		"roles": ["Pharma Regulatory Officer", "Purchase Manager"],
		"commerce_role": "commerce_purchasing",
		"label_en": "Import Manager Portal",
		"label_ar": "بوابة مدير الاستيراد",
		"role_en": "Import Manager",
		"role_ar": "مدير الاستيراد",
		"menu_sections": [_IMPORT_EXPORT_MENU, _PHARMA_OPS_MENU],
	},
	{
		"key": "export-manager",
		"page": "trading-export-manager",
		"route": "/app/trading-export-manager",
		"icon": "📤",
		"category": "operations",
		"roles": ["Pharma Regulatory Officer", "Sales Manager"],
		"commerce_role": "commerce_sales",
		"label_en": "Export Manager Portal",
		"label_ar": "بوابة مدير التصدير",
		"role_en": "Export Manager",
		"role_ar": "مدير التصدير",
		"menu_sections": [
			_section("Export Operations", "عمليات التصدير", [
				_menu_item("Export Shipment", "شحنات التصدير", _dt_route("Pharma Export Shipment"), "📤"),
				_menu_item("Regulatory Approval", "الموافقات", _dt_route("Pharma Regulatory Approval"), "🏛️"),
				_menu_item("Drug Registration", "تسجيل الأدوية", _dt_route("Pharma Drug Registration"), "📝"),
				_menu_item("Sales Invoice", "فواتير التصدير", _dt_route("Sales Invoice"), "🧾"),
			]),
			_PHARMA_OPS_MENU,
		],
	},
	{
		"key": "quality-manager",
		"page": "trading-quality-manager",
		"route": "/app/trading-quality-manager",
		"icon": "🔬",
		"category": "compliance",
		"roles": ["Pharma Quality Manager"],
		"commerce_role": "commerce_inventory",
		"label_en": "Quality Manager Portal",
		"label_ar": "بوابة مدير الجودة",
		"role_en": "Quality Manager",
		"role_ar": "مدير الجودة",
		"menu_sections": [
			_section("Quality Control (GMP)", "مراقبة الجودة", [
				_menu_item("Quality Inspection", "فحص الجودة", _dt_route("Pharma Quality Inspection"), "🔬"),
				_menu_item("Pharma Batch", "دفعات الأدوية", _dt_route("Pharma Batch"), "💊"),
				_menu_item("Product Recall", "الاستدعاء", _dt_route("Pharma Product Recall"), "🔄"),
				_menu_item("Equipment Qualification", "تأهيل المعدات", _dt_route("Equipment Qualification"), "⚙️"),
			]),
			_COMPLIANCE_MENU,
		],
	},
	{
		"key": "cold-chain-manager",
		"page": "trading-cold-chain-manager",
		"route": "/app/trading-cold-chain-manager",
		"icon": "❄️",
		"category": "compliance",
		"roles": ["Pharma Cold Chain Manager"],
		"commerce_role": "commerce_warehouse",
		"label_en": "Cold Chain Manager Portal",
		"label_ar": "بوابة مدير السلسلة الباردة",
		"role_en": "Cold Chain Manager",
		"role_ar": "مدير السلسلة الباردة",
		"menu_sections": [_COLD_CHAIN_MENU, _WAREHOUSE_MENU],
	},
	{
		"key": "regulatory-officer",
		"page": "trading-regulatory-officer",
		"route": "/app/trading-regulatory-officer",
		"icon": "🏛️",
		"category": "compliance",
		"roles": ["Pharma Regulatory Officer"],
		"commerce_role": "commerce_purchasing",
		"label_en": "Regulatory Officer Portal",
		"label_ar": "بوابة الشؤون التنظيمية",
		"role_en": "Regulatory Officer",
		"role_ar": "موظف الشؤون التنظيمية",
		"menu_sections": [
			_section("Regulatory Affairs", "الشؤون التنظيمية", [
				_menu_item("Regulatory Approval", "الموافقات", _dt_route("Pharma Regulatory Approval"), "🏛️"),
				_menu_item("Drug Registration", "تسجيل الأدوية", _dt_route("Pharma Drug Registration"), "📝"),
				_menu_item("Drug License", "التراخيص", _dt_route("Pharma Drug License"), "📜"),
				_menu_item("Import License", "تراخيص الاستيراد", _dt_route("Pharma Import License"), "📥"),
			]),
			_COMPLIANCE_MENU,
		],
	},
	{
		"key": "inventory-controller",
		"page": "trading-inventory-controller",
		"route": "/app/trading-inventory-controller",
		"icon": "📦",
		"category": "operations",
		"roles": ["Stock User", "Pharma Warehouse Manager"],
		"commerce_role": "commerce_inventory",
		"label_en": "Inventory Controller Portal",
		"label_ar": "بوابة مراقب المخزون",
		"role_en": "Inventory Controller",
		"role_ar": "مراقب المخزون",
		"menu_sections": [_WAREHOUSE_MENU, _PHARMA_OPS_MENU],
	},
	{
		"key": "sales-director",
		"page": "trading-sales-director",
		"route": "/app/trading-sales-director",
		"icon": "💼",
		"category": "sales",
		"roles": ["Sales Manager"],
		"commerce_role": "commerce_sales",
		"label_en": "Sales Director Portal",
		"label_ar": "بوابة مدير المبيعات",
		"role_en": "Sales Director",
		"role_ar": "مدير المبيعات",
		"menu_sections": [_SALES_MENU, _section("Commissions", "العمولات", [
			_menu_item("Commission Rule", "قواعد العمولة", _dt_route("Trading Commission Rule"), "💰"),
			_menu_item("Commission Settlement", "تسوية العمولات", _dt_route("Trading Commission Settlement"), "📊"),
			_menu_item("Commission Summary", "ملخص العمولات", _report_route("Trading Commission Summary"), "📈"),
		])],
	},
	{
		"key": "medical-rep",
		"page": "trading-van-sales-pwa",
		"route": "/app/trading-van-sales-pwa",
		"icon": "🚚",
		"category": "field",
		"roles": ["Pharma Sales Representative", "Sales User"],
		"commerce_role": "commerce_sales",
		"label_en": "Medical Representative Portal",
		"label_ar": "بوابة المندوب الطبي",
		"role_en": "Medical Representative",
		"role_ar": "المندوب الطبي",
		"menu_sections": [_SALES_MENU, _section("Field Operations", "العمليات الميدانية", [
			_menu_item("Van Sales Invoice", "فواتير المندوب", _dt_route("Trading Van Sales Invoice"), "🚐"),
			_menu_item("Route Plan", "خط السير", _dt_route("Trading Route Plan"), "🗺️"),
			_menu_item("Vehicle Stock Transfer", "تحويل مخزون المركبة", _dt_route("Trading Vehicle Stock Transfer"), "🚚"),
			_menu_item("Sample Register", "عينات الأدوية", _dt_route("Pharma Sample Register"), "🧪"),
		])],
	},
	{
		"key": "chief-accountant",
		"page": "trading-finance-desk",
		"route": "/app/trading-finance-desk",
		"icon": "💰",
		"category": "finance",
		"roles": ["Pharma Finance Manager", "Accounts Manager", "Accounts User"],
		"commerce_role": "commerce_finance",
		"label_en": "Chief Accountant Portal",
		"label_ar": "بوابة المحاسب الرئيسي",
		"role_en": "Chief Accountant",
		"role_ar": "المحاسب الرئيسي",
		"menu_sections": [_FINANCE_MENU],
	},
	{
		"key": "auditor",
		"page": "trading-auditor",
		"route": "/app/trading-auditor",
		"icon": "🔍",
		"category": "compliance",
		"roles": ["Auditor", "System Manager"],
		"commerce_role": "commerce_system_administrator",
		"label_en": "Auditor Portal",
		"label_ar": "بوابة المدقق",
		"role_en": "Auditor",
		"role_ar": "المدقق",
		"menu_sections": [
			_COMPLIANCE_MENU,
			_section("Audit & Reports", "التدقيق والتقارير", [
				_menu_item("Audit Log", "سجل التدقيق", _dt_route("Audit Log"), "📋"),
				_menu_item("Field Change", "تغييرات الحقول", _dt_route("Field Change"), "📝"),
				_menu_item("General Ledger", "دفتر الأستاذ", _report_route("General Ledger"), "📊"),
			]),
		],
	},
	{
		"key": "operations-director",
		"page": "trading-operations-director",
		"route": "/app/trading-operations-director",
		"icon": "⚙️",
		"category": "operations",
		"roles": ["Sales User", "Stock User", "Purchase User"],
		"commerce_role": "commerce_inventory",
		"label_en": "Operations Director Portal",
		"label_ar": "بوابة مدير العمليات",
		"role_en": "Operations Director",
		"role_ar": "مدير العمليات",
		"menu_sections": [_PHARMA_OPS_MENU, _WAREHOUSE_MENU, _SALES_MENU, _IMPORT_EXPORT_MENU],
	},
	{
		"key": "finance-director",
		"page": "trading-finance-director",
		"route": "/app/trading-finance-director",
		"icon": "💼",
		"category": "finance",
		"roles": ["Pharma Finance Manager", "Accounts Manager"],
		"commerce_role": "commerce_finance",
		"label_en": "Finance Director Portal",
		"label_ar": "بوابة المدير المالي",
		"role_en": "Finance Director",
		"role_ar": "المدير المالي",
		"menu_sections": [_FINANCE_MENU, _section("Credit & Installments", "الائتمان والتقسيط", [
			_menu_item("Installment Contract", "عقود التقسيط", _dt_route("Trading Installment Contract"), "💰"),
			_menu_item("Installment Portfolio", "محفظة التقسيط", _report_route("Trading Installment Portfolio"), "📊"),
		])],
	},
	{
		"key": "hr-director",
		"page": "trading-hr-director",
		"route": "/app/trading-hr-director",
		"icon": "👥",
		"category": "hr",
		"roles": ["HR Manager", "HR User"],
		"commerce_role": "commerce_hr",
		"label_en": "HR Director Portal",
		"label_ar": "بوابة مدير الموارد البشرية",
		"role_en": "HR Director",
		"role_ar": "مدير الموارد البشرية",
		"menu_sections": [_HR_MENU, _COMPLIANCE_MENU],
	},
	{
		"key": "area-manager",
		"page": "trading-area-manager",
		"route": "/app/trading-area-manager",
		"icon": "🗺️",
		"category": "sales",
		"roles": ["Sales Manager", "Sales User"],
		"commerce_role": "commerce_sales",
		"label_en": "Area Manager Portal",
		"label_ar": "بوابة مدير المنطقة",
		"role_en": "Area Manager",
		"role_ar": "مدير المنطقة",
		"menu_sections": [_SALES_MENU, _section("Territory", "المنطقة", [
			_menu_item("Distribution Zone", "مناطق التوزيع", _dt_route("Distribution Zone"), "🗺️"),
			_menu_item("Route Plan", "خطط المسارات", _dt_route("Trading Route Plan"), "📍"),
			_menu_item("Rep Target Tracking", "أهداف المندوبين", _report_route("Trading Rep Target Tracking"), "🎯"),
		])],
	},
	{
		"key": "sales-supervisor",
		"page": "trading-sales-supervisor",
		"route": "/app/trading-sales-supervisor",
		"icon": "📋",
		"category": "sales",
		"roles": ["Sales User", "Sales Manager"],
		"commerce_role": "commerce_sales",
		"label_en": "Sales Supervisor Portal",
		"label_ar": "بوابة مشرف المبيعات",
		"role_en": "Sales Supervisor",
		"role_ar": "مشرف المبيعات",
		"menu_sections": [_SALES_MENU, _section("Team Performance", "أداء الفريق", [
			_menu_item("Van Sales Invoice", "فواتير المندوبين", _dt_route("Trading Van Sales Invoice"), "🚐"),
			_menu_item("Commission Summary", "ملخص العمولات", _report_route("Trading Commission Summary"), "💰"),
			_menu_item("Route Efficiency", "كفاءة المسارات", _report_route("Trading Route Efficiency"), "📈"),
		])],
	},
	{
		"key": "customer-service",
		"page": "trading-customer-service",
		"route": "/app/trading-customer-service",
		"icon": "🎧",
		"category": "customer",
		"roles": ["Customer", "Sales User"],
		"commerce_role": "commerce_customer_service",
		"label_en": "Customer Service Portal",
		"label_ar": "بوابة خدمة العملاء",
		"role_en": "Customer Service",
		"role_ar": "خدمة العملاء",
		"menu_sections": [_section("Customer Care", "رعاية العملاء", [
			_menu_item("Customer", "العملاء", _dt_route("Customer"), "👥"),
			_menu_item("Issue", "البلاغات", _dt_route("Issue"), "🎫"),
			_menu_item("Product Recall", "استدعاء المنتجات", _dt_route("Pharma Product Recall"), "🔄"),
			_menu_item("Sales Order", "أوامر المبيعات", _dt_route("Sales Order"), "🛍️"),
		])],
	},
	{
		"key": "treasury",
		"page": "trading-treasury",
		"route": "/app/trading-treasury",
		"icon": "🏦",
		"category": "finance",
		"roles": ["Accounts Manager", "Accounts User"],
		"commerce_role": "commerce_finance",
		"label_en": "Treasury Portal",
		"label_ar": "بوابة الخزينة",
		"role_en": "Treasury",
		"role_ar": "الخزينة",
		"menu_sections": [_section("Treasury", "الخزينة", [
			_menu_item("Payment Entry", "سندات القبض/الصرف", _dt_route("Payment Entry"), "💳"),
			_menu_item("Journal Entry", "قيود اليومية", _dt_route("Journal Entry"), "📒"),
			_menu_item("Import LC", "خطابات الاعتماد", _dt_route("Pharma Import LC"), "🏦"),
			_menu_item("General Ledger", "دفتر الأستاذ", _report_route("General Ledger"), "📊"),
		])],
	},
	{
		"key": "cashier",
		"page": "trading-cashier",
		"route": "/app/trading-cashier",
		"icon": "💵",
		"category": "finance",
		"roles": ["Accounts User"],
		"commerce_role": "commerce_pos_cashier",
		"label_en": "Cashier Portal",
		"label_ar": "بوابة أمين الصندوق",
		"role_en": "Cashier",
		"role_ar": "أمين الصندوق",
		"menu_sections": [_section("Cash Operations", "عمليات الصندوق", [
			_menu_item("Payment Entry", "سندات القبض", _dt_route("Payment Entry"), "💳"),
			_menu_item("Sales Invoice", "فواتير المبيعات", _dt_route("Sales Invoice"), "🧾"),
			_menu_item("POS Z Reconciliation", "تسوية POS", _report_route("POS Z Report Reconciliation"), "📊"),
		])],
	},
	{
		"key": "store-keeper",
		"page": "trading-store-keeper",
		"route": "/app/trading-store-keeper",
		"icon": "📦",
		"category": "operations",
		"roles": ["Stock User"],
		"commerce_role": "commerce_warehouse",
		"label_en": "Store Keeper Portal",
		"label_ar": "بوابة أمين المخزن",
		"role_en": "Store Keeper",
		"role_ar": "أمين المخزن",
		"menu_sections": [_WAREHOUSE_MENU, _PHARMA_OPS_MENU],
	},
	{
		"key": "dispatch",
		"page": "trading-dispatch",
		"route": "/app/trading-dispatch",
		"icon": "🚚",
		"category": "operations",
		"roles": ["Stock User", "Pharma Warehouse Manager"],
		"commerce_role": "commerce_warehouse",
		"label_en": "Dispatch Portal",
		"label_ar": "بوابة التسليم",
		"role_en": "Dispatch",
		"role_ar": "التسليم",
		"menu_sections": [_DISPATCH_MENU, _COLD_CHAIN_MENU],
	},
	{
		"key": "receiving",
		"page": "trading-receiving",
		"route": "/app/trading-receiving",
		"icon": "📥",
		"category": "operations",
		"roles": ["Stock User", "Purchase User"],
		"commerce_role": "commerce_warehouse",
		"label_en": "Receiving Portal",
		"label_ar": "بوابة الاستلام",
		"role_en": "Receiving",
		"role_ar": "الاستلام",
		"menu_sections": [_RECEIVING_MENU, _PHARMA_OPS_MENU],
	},
	{
		"key": "executive-dashboard",
		"page": "trading-executive-dashboard",
		"route": "/app/trading-executive-dashboard",
		"icon": "📊",
		"category": "management",
		"roles": ["Company Admin", "Sales Manager"],
		"commerce_role": "commerce_general_manager",
		"label_en": "Executive Dashboard",
		"label_ar": "لوحة الإدارة التنفيذية",
		"role_en": "Executive",
		"role_ar": "الإدارة التنفيذية",
		"menu_sections": [_EXECUTIVE_MENU, _POS_MENU, _PHARMA_OPS_MENU, _SALES_MENU, _FINANCE_MENU, _COMPLIANCE_MENU],
	},
	{
		"key": "workcenter",
		"page": "trading-workcenter",
		"route": "/app/trading-workcenter",
		"icon": "🏢",
		"category": "admin",
		"roles": ["System Manager", "Company Admin"],
		"commerce_role": "commerce_system_administrator",
		"label_en": "Trading Workcenter",
		"label_ar": "مركز عمل التجارة",
		"role_en": "System Administrator",
		"role_ar": "مدير النظام",
		"menu_sections": [
			_section("Administration", "الإدارة", [
				_menu_item("All Role Portals", "جميع البوابات", "/app/trading-executive-dashboard", "🌐"),
				_menu_item("Trading Workspace", "مساحة التجارة", "/app/trading", "📁"),
				_menu_item("Omnexa Sales Settings", "إعدادات المبيعات", _dt_route("Omnexa Sales Settings"), "⚙️"),
				_menu_item("Audit Log", "سجل التدقيق", _dt_route("Audit Log"), "📋"),
			]),
			_EXECUTIVE_MENU,
		],
	},
]

CATEGORY_LABELS = {
	"admin": {"ar": "الإدارة", "en": "Administration"},
	"management": {"ar": "الإدارة التنفيذية", "en": "Management"},
	"operations": {"ar": "العمليات", "en": "Operations"},
	"compliance": {"ar": "الامتثال والجودة", "en": "Compliance & Quality"},
	"sales": {"ar": "المبيعات", "en": "Sales"},
	"finance": {"ar": "المالية", "en": "Finance"},
	"field": {"ar": "الميدان", "en": "Field Sales"},
	"customer": {"ar": "العملاء", "en": "Customer"},
	"hr": {"ar": "الموارد البشرية", "en": "Human Resources"},
}

_ROLE_ALIASES = {
	"operations-desk": "operations-director",
	"system-administrator": "workcenter",
	"system_administrator": "workcenter",
}


def get_portal_by_key(role_key: str) -> dict | None:
	if not role_key:
		return None
	role_key = _ROLE_ALIASES.get(role_key, role_key)
	for portal in PHARMA_ROLE_PORTALS:
		if portal["key"] == role_key or portal["page"].endswith(role_key.replace("_", "-")):
			return portal
	return None


def get_portal_for_user(user: str | None = None) -> dict | None:
	user = user or frappe.session.user
	user_roles = set(frappe.get_roles(user))
	for portal in PHARMA_ROLE_PORTALS:
		if user_roles.intersection(portal.get("roles", [])):
			return portal
	if user == "Administrator" or "System Manager" in user_roles:
		return get_portal_by_key("workcenter")
	return None


@frappe.whitelist()
def get_pharma_portal_catalog(include_missing: int = 0) -> list[dict]:
	from frappe.utils import cint

	out = []
	for row in PHARMA_ROLE_PORTALS:
		item = dict(row)
		item["exists"] = bool(frappe.db.exists("Page", item["page"]))
		if item["exists"] or cint(include_missing):
			out.append(item)
	return out


@frappe.whitelist()
def get_grouped_pharma_portal_catalog(include_missing: int = 0) -> list[dict]:
	from frappe.utils import cint

	groups: dict[str, list] = {}
	for row in get_pharma_portal_catalog(include_missing=cint(include_missing)):
		groups.setdefault(row["category"], []).append(row)
	result = []
	for cat, portals in groups.items():
		labels = CATEGORY_LABELS.get(cat, {"ar": cat, "en": cat})
		result.append({"category": cat, "label_ar": labels["ar"], "label_en": labels["en"], "portals": portals})
	return result


@frappe.whitelist()
def get_role_portal_context(role_key: str | None = None) -> dict:
	from omnexa_core.omnexa_core.app_logo_registry import get_logo_url

	portal = get_portal_by_key(role_key or "") if role_key else get_portal_for_user()
	if not portal:
		portal = get_portal_by_key("operations-director") or PHARMA_ROLE_PORTALS[0]

	multi_portal = {}
	dashboard = {}
	try:
		from omnexa_core.multi_portal.portal_factory import PortalFactory
		from omnexa_core.multi_portal.serialization import to_serializable

		commerce_role = portal.get("commerce_role")
		if commerce_role:
			multi_portal = to_serializable(PortalFactory().create_portal("commerce", commerce_role))
	except Exception:
		pass

	try:
		from omnexa_trading.pharma_portal_dashboard import get_role_portal_dashboard

		dashboard = get_role_portal_dashboard(portal["key"])
	except Exception:
		pass

	return {
		"portal": portal,
		"menu_sections": portal.get("menu_sections", []),
		"dashboard": dashboard,
		"logo_url": get_logo_url("omnexa_trading"),
		"multi_portal": multi_portal,
		"workcenter_route": "/app/trading-workcenter",
		"title_en": "Omnexa Trading — Pharmaceutical",
		"title_ar": "Omnexa Trading — تجارة وتوزيع الأدوية",
	}
