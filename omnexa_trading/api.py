from __future__ import annotations

import frappe


@frappe.whitelist()
def get_site_config() -> dict:
	"""Return public website configuration for trading site."""
	return {
		"brand_name_ar": "Omnexa Trading",
		"brand_name_en": "Omnexa Trading",
		"tagline_ar": "حلول تجارية متكاملة لإدارة سلسلة التوريد",
		"tagline_en": "Integrated trading solutions for supply chain management",
		"hero_text_ar": "من إدارة المخزون إلى نقاط البيع — منصة واحدة لكل عملياتك التجارية",
		"hero_text_en": "From inventory management to point of sale — one platform for all your trading operations",
		"hero_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1920&q=85",
		"logo": "/assets/omnexa_trading/logo.png",
		"primary_color": "#003366",
		"secondary_color": "#0A5FA8",
		"accent_color": "#00B4D8",
		"gold_color": "#D4AF37",
		"categories": [
			{"key": "pharma", "name_ar": "الأدوية والمستحضرات", "name_en": "Pharmaceuticals", "icon": "💊", "count": 1500},
			{"key": "medical", "name_ar": "المعدات الطبية", "name_en": "Medical Equipment", "icon": "🏥", "count": 800},
			{"key": "food", "name_ar": "الأغذية والمشروبات", "name_en": "Food & Beverages", "icon": "🍎", "count": 2000},
			{"key": "cosmetics", "name_ar": "التجميل والعناية", "name_en": "Cosmetics & Care", "icon": "✨", "count": 500},
		],
		"features": [
			{"icon": "📦", "ar": "إدارة المخزون", "en": "Inventory Management"},
			{"icon": "🚚", "ar": "التوزيع والنقل", "en": "Distribution & Logistics"},
			{"icon": "📊", "ar": "تحليلات المبيعات", "en": "Sales Analytics"},
			{"icon": "🔒", "ar": "تتبع المنتجات", "en": "Product Tracking"},
			{"icon": "💳", "ar": "نقاط البيع", "en": "Point of Sale"},
			{"icon": "📱", "ar": "تطبيق المبيعات", "en": "Mobile Sales"},
		],
		"stats": {"products": 5000, "suppliers": 200, "customers": 10000, "branches": 50},
	}


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("trading", scenario=scenario, params=params)
