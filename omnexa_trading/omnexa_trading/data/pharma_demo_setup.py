#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pharmaceutical Trading Demo Setup Script
Creates a complete demo environment for pharmaceutical trading company
"""

import frappe
import random
from frappe.utils import today, add_days, getdate
from frappe.model.rename_doc import rename_doc


def _log(message):
	"""Progress log safe for bench execute and whitelisted API calls."""
	msg = str(message)
	try:
		frappe.logger("pharma_demo_setup").info(msg)
	except Exception:
		pass
	try:
		print(msg, flush=True)
	except BrokenPipeError:
		pass
	except OSError as exc:
		if exc.errno != 32:
			raise


def create_pharma_company():
    """Create pharmaceutical trading company"""
    company_name = "PharmaTrade Egypt Ltd."
    
    if frappe.db.exists("Company", company_name):
        _log(f"Company already exists: {company_name}")
        return frappe.get_doc("Company", company_name)
    
    # Try with different abbr if PTE exists
    if frappe.db.exists("Company", {"abbr": "PTE"
	}):
        company = frappe.get_doc("Company", {"abbr": "PTE"
	})
        _log(f"Using existing company with abbr PTE: {company.name}")
        return company
    
    company = frappe.get_doc({
        "doctype": "Company",
        "company_name": company_name,
        "abbr": "PTE",
        "country": "Egypt",
        "default_currency": "EGP",
        "default_gst_rate": 14,
        "industry_sector": "Trading",
        "enable_perpetual_inventory": 1,
        "default_finance_book": "Standard",
        "email": "info@pharmatrade-egypt.com",
        "phone": "+20 2 12345678",
        "website": "www.pharmatrade-egypt.com",
        "tax_id": "123456789012345",
        "address": "Cairo, Egypt"
    })
    company.insert()
    _log(f"Created company: {company_name}")
    return company

def create_pharma_branch(company):
    """Create head office branch with pharmaceutical trading activity"""
    branch_name = f"{company.abbr}-HO"
    
    if frappe.db.exists("Branch", branch_name):
        _log(f"Branch already exists: {branch_name}")
        return frappe.get_doc("Branch", branch_name)
    
    branch = frappe.get_doc({
        "doctype": "Branch",
        "branch_name": "Head Office - Cairo",
        "branch_code": "HO",
        "company": company.name,
        "is_head_office": 1,
        "status": "Active",
        "country_code": "EG",
        "default_vat_rate": 14,
        "branch_demo_activity": "Pharmaceutical Trading (تجارة وتوزيع الأدوية)",
        "branch_demo_include_workspace_seed": 1,
        "branch_demo_daily_purchase_invoices": 15,
        "branch_demo_daily_sales_invoices": 20,
        "branch_demo_employees": 10,
        "branch_demo_customers": 30,
        "branch_demo_suppliers": 20,
        "branch_demo_items": 50
    })
    branch.insert()
    _log(f"Created branch: {branch_name}")
    return branch

def create_pharma_roles():
    """Create pharmaceutical trading specific roles"""
    roles = [
        {
            "role_name": "Pharma Warehouse Manager",
            "desk_access": 1,
            "is_standard": 0,
            "description": "مدير مستودع الأدوية - Warehouse Manager for Pharmaceuticals"
        },
        {
            "role_name": "Pharma Quality Manager",
            "desk_access": 1,
            "is_standard": 0,
            "description": "مدير الجودة - Quality Manager for Pharmaceuticals"
        },
        {
            "role_name": "Pharma Sales Representative",
            "desk_access": 1,
            "is_standard": 0,
            "description": "مندوب مبيعات الأدوية - Sales Representative for Pharmaceuticals"
        },
        {
            "role_name": "Pharma Regulatory Officer",
            "desk_access": 1,
            "is_standard": 0,
            "description": "موظف الشؤون التنظيمية - Regulatory Officer for Pharmaceuticals"
        },
        {
            "role_name": "Pharma Cold Chain Manager",
            "desk_access": 1,
            "is_standard": 0,
            "description": "مدير السلسلة الباردة - Cold Chain Manager for Pharmaceuticals"
        },
        {
            "role_name": "Pharma Finance Manager",
            "desk_access": 1,
            "is_standard": 0,
            "description": "مدير المالية للصيدلة - Finance Manager for Pharmaceuticals"
        }
    ]
    
    created_roles = []
    for role_data in roles:
        if frappe.db.exists("Role", role_data["role_name"]):
            _log(f"Role already exists: {role_data['role_name']}")
            created_roles.append(frappe.get_doc("Role", role_data["role_name"]))
            continue
        
        role = frappe.get_doc({
            "doctype": "Role",
            **role_data
        })
        role.insert()
        created_roles.append(role)
        _log(f"Created role: {role_data['role_name']}")
    
    return created_roles

def create_pharma_users(company, branch, roles):
    """Create demo users for pharmaceutical trading roles"""
    users_data = [
        {
            "email": "pharma.warehouse.manager@pharmatrade-egypt.com",
            "first_name": "Ahmed",
            "last_name": "Mohamed",
            "role": "Pharma Warehouse Manager",
            "password": "Pharma@Demo2026"
        },
        {
            "email": "pharma.quality.manager@pharmatrade-egypt.com",
            "first_name": "Sara",
            "last_name": "Ali",
            "role": "Pharma Quality Manager",
            "password": "Pharma@Demo2026"
        },
        {
            "email": "pharma.sales.rep@pharmatrade-egypt.com",
            "first_name": "Omar",
            "last_name": "Hassan",
            "role": "Pharma Sales Representative",
            "password": "Pharma@Demo2026"
        },
        {
            "email": "pharma.regulatory.officer@pharmatrade-egypt.com",
            "first_name": "Layla",
            "last_name": "Ibrahim",
            "role": "Pharma Regulatory Officer",
            "password": "Pharma@Demo2026"
        },
        {
            "email": "pharma.cold.chain.manager@pharmatrade-egypt.com",
            "first_name": "Kareem",
            "last_name": "Fathy",
            "role": "Pharma Cold Chain Manager",
            "password": "Pharma@Demo2026"
        },
        {
            "email": "pharma.finance.manager@pharmatrade-egypt.com",
            "first_name": "Nour",
            "last_name": "Said",
            "role": "Pharma Finance Manager",
            "password": "Pharma@Demo2026"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        if frappe.db.exists("User", user_data["email"]):
            _log(f"User already exists: {user_data['email']}")
            user = frappe.get_doc("User", user_data["email"])
            created_users.append(user)
            continue
        
        user = frappe.get_doc({
            "doctype": "User",
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "enabled": 1,
            "send_welcome_email": 0,
            "new_password": user_data["password"]
        })
        user.insert()
        
        # Add role to user
        user.append("roles", {"role": user_data["role"]
	})
        user.save()
        
        # Add user branch access
        user_branch = frappe.get_doc({
            "doctype": "User Branch Access",
            "user": user.name,
            "branch": branch.name,
            "company": company.name
        })
        user_branch.insert()
        
        created_users.append(user)
        _log(f"Created user: {user_data['email']} - {user_data['role']}")
    
    return created_users

def create_pharma_portals():
	"""Create pharmaceutical trading role portal pages."""
	from omnexa_trading.pharma_portal_scaffold import scaffold_pharma_portals

	portals = scaffold_pharma_portals(skip_existing_js=False)
	_log(f"Scaffolded {len(portals)} pharma role portals")
	return portals


def create_pharma_workspaces():
	"""Sync trading workspace with pharma compliance sections."""
	from omnexa_trading.patches.v1_0.remove_pharma_warehouse_management_workspace import execute as remove_legacy_workspace
	from omnexa_trading.workspace.trading_workspace import sync_trading_workspace_menu

	remove_legacy_workspace()
	stats = sync_trading_workspace_menu(save=True, rebuild=True)
	_log(f"Trading workspace synced: {stats}")
	return [stats]

def seed_pharma_demo_data(company, branch):
    """Seed pharmaceutical trading demo data"""
    _log("\n" + "=" * 50)
    _log("Seeding Pharmaceutical Trading Demo Data")
    _log("=" * 50)
    
    # Import demo data functions
    from omnexa_trading.omnexa_trading.data.demo_data import (
        create_demo_suppliers,
        create_demo_customers,
        create_demo_warehouses,
        create_demo_item_groups
    )
    
    _log("\n1. Creating item groups...")
    item_groups = create_demo_item_groups()
    
    _log("\n2. Creating demo suppliers...")
    suppliers = create_demo_suppliers()
    
    _log("\n3. Creating demo customers...")
    customers = create_demo_customers()
    
    _log("\n4. Creating specialized warehouses...")
    warehouses = create_demo_warehouses()
    
    _log("\n" + "=" * 50)
    _log("Demo Data Seeding Summary")
    _log("=" * 50)
    _log(f"Item Groups: {item_groups}")
    _log(f"Suppliers: {suppliers}")
    _log(f"Customers: {customers}")
    _log(f"Warehouses: {warehouses}")
    _log("=" * 50)
    
    return {
        "item_groups": item_groups,
        "suppliers": suppliers,
        "customers": customers,
        "warehouses": warehouses
    }


def seed_pharma_operational_transactions(company):
	"""Seed import/export/quality transactions for global pharma demo realism."""
	from frappe.utils import add_days, today

	created = {"batches": 0, "import_licenses": 0, "export_shipments": 0, "quality_inspections": 0
	}
	if not company:
		return created

	item_code = frappe.db.get_value("Item", {"is_stock_item": 1
	}, "name")
	uom = frappe.db.get_value("Item", item_code, "stock_uom") if item_code else "Nos"
	if not item_code:
		item_code = frappe.db.get_value("Item", {}, "name")
		uom = frappe.db.get_value("Item", item_code, "stock_uom") if item_code else "Nos"

	if frappe.db.count("Pharma Batch") == 0 and frappe.db.exists("DocType", "Pharma Batch") and item_code:
		for idx in range(1, 6):
			try:
				doc = frappe.get_doc({
					"doctype": "Pharma Batch",
					"batch_number": f"PTE-DEMO-{idx:03d
	}",
					"item_code": item_code,
					"company": company,
					"manufacturing_date": add_days(today(), -120),
					"expiry_date": add_days(today(), 365),
					"batch_size": 1000 + idx * 100,
					"uom": uom or "Nos",
					"status": "Released",
					"cold_chain_required": 1 if idx % 2 == 0 else 0
	})
				doc.insert(ignore_permissions=True)
				created["batches"] += 1
			except Exception as exc:
				_log(f"Pharma batch seed skipped {idx}: {exc}")

	if frappe.db.count("Pharma Import License") == 0 and frappe.db.exists("DocType", "Pharma Import License"):
		for idx in range(1, 4):
			try:
				doc = frappe.get_doc({
					"doctype": "Pharma Import License",
					"license_number": f"IMP-PTE-{idx:03d
	}",
					"license_type": "Drug Import License",
					"company": company,
					"issue_date": add_days(today(), -30),
					"expiry_date": add_days(today(), 335),
					"status": "Active",
					"country_of_origin": "Germany"
	})
				doc.insert(ignore_permissions=True)
				created["import_licenses"] += 1
			except Exception as exc:
				_log(f"Import license seed skipped {idx}: {exc}")

	if frappe.db.count("Pharma Export Shipment") == 0 and frappe.db.exists("DocType", "Pharma Export Shipment"):
		for idx in range(1, 4):
			try:
				doc = frappe.get_doc({
					"doctype": "Pharma Export Shipment",
					"company": company,
					"shipment_date": add_days(today(), -7 * idx),
					"destination_country": "Saudi Arabia",
					"status": "In Transit" if idx == 1 else "Delivered"
	})
				doc.insert(ignore_permissions=True)
				created["export_shipments"] += 1
			except Exception as exc:
				_log(f"Export shipment seed skipped {idx}: {exc}")

	if frappe.db.count("Pharma Quality Inspection") == 0 and frappe.db.exists("DocType", "Pharma Quality Inspection"):
		batch = frappe.db.get_value("Pharma Batch", {}, "batch_number")
		if batch and item_code:
			try:
				doc = frappe.get_doc({
					"doctype": "Pharma Quality Inspection",
					"inspection_number": "QC-PTE-001",
					"company": company,
					"item_code": item_code,
					"batch_number": batch,
					"inspection_date": today(),
					"inspection_type": "Incoming",
					"status": "Approved"
	})
				doc.insert(ignore_permissions=True)
				created["quality_inspections"] += 1
			except Exception as exc:
				_log(f"Quality inspection seed skipped: {exc}")

	frappe.db.commit()
	_log(f"Pharma operational transactions: {created}")
	return created

def run_pharma_demo_setup():
    """Run complete pharmaceutical trading demo setup"""
    _log("\n" + "=" * 60)
    _log("PHARMACEUTICAL TRADING DEMO SETUP")
    _log("=" * 60)
    
    try:
        # Step 1: Create Company
        _log("\n[Step 1/6] Creating Pharmaceutical Trading Company...")
        company = create_pharma_company()
        
        # Step 2: Create Branch
        _log("\n[Step 2/6] Creating Head Office Branch...")
        branch = create_pharma_branch(company)
        
        # Step 3: Create Roles
        _log("\n[Step 3/6] Creating Pharmaceutical Trading Roles...")
        roles = create_pharma_roles()
        
        # Step 4: Create Users
        _log("\n[Step 4/6] Creating Demo Users...")
        users = create_pharma_users(company, branch, roles)
        
        # Step 5: Create Portals
        _log("\n[Step 5/6] Creating Role Portals...")
        portals = create_pharma_portals()
        
        # Step 6: Create Workspaces
        _log("\n[Step 6/6] Creating Workspaces...")
        workspaces = create_pharma_workspaces()
        
        # Step 7: Seed Demo Data
        _log("\n[Step 7/7] Seeding Demo Data...")
        demo_data = seed_pharma_demo_data(company, branch)

        # Step 8: Seed operational transactions
        _log("\n[Step 8/8] Seeding Import/Export/Quality Transactions...")
        transactions = seed_pharma_operational_transactions(company.name)
        demo_data["transactions"] = transactions
        
        _log("\n" + "=" * 60)
        _log("PHARMACEUTICAL TRADING DEMO SETUP COMPLETED")
        _log("=" * 60)
        _log(f"\nCompany: {company.name}")
        _log(f"Branch: {branch.name}")
        _log(f"Roles Created: {len(roles)}")
        _log(f"Users Created: {len(users)}")
        _log(f"Portals Created: {len(portals)}")
        _log(f"Workspaces Created: {len(workspaces)}")
        _log(f"\nDemo Data:")
        _log(f"  - Item Groups: {demo_data['item_groups']}")
        _log(f"  - Suppliers: {demo_data['suppliers']}")
        _log(f"  - Customers: {demo_data['customers']}")
        _log(f"  - Warehouses: {demo_data['warehouses']}")
        _log("\n" + "=" * 60)
        _log("DEMO USERS LOGIN CREDENTIALS")
        _log("=" * 60)
        _log("All demo users use password: Pharma@Demo2026")
        _log("\nUsers:")
        for user in users:
            _log(f"  - {user.email} ({user.first_name} {user.last_name})")
        _log("=" * 60)
        
        return {
            "company": company.name,
            "branch": branch.name,
            "roles": len(roles),
            "users": len(users),
            "portals": len(portals),
            "workspaces": len(workspaces),
            "demo_data": demo_data
        }
        
    except Exception as e:
        _log(f"\nError during demo setup: {e}")
        frappe.log_error(title="Pharma Demo Setup Failed", message=frappe.get_traceback())
        return None

if __name__ == "__main__":
    run_pharma_demo_setup()
